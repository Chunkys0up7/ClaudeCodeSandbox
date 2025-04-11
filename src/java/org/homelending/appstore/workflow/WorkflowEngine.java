package org.homelending.appstore.workflow;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Function;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Java implementation of the Workflow Engine for the AI App Store
 * Provides functionality for creating, managing and executing workflows
 */
public class WorkflowEngine {
    private static final Logger logger = Logger.getLogger(WorkflowEngine.class.getName());
    
    private final Map<String, Workflow> workflows;
    private final Map<String, WorkflowExecution> executions;
    private final Map<String, Map<String, Function<Map<String, Object>, Map<String, Object>>>> componentRegistry;
    
    /**
     * Initialize the workflow engine
     */
    public WorkflowEngine() {
        this.workflows = new ConcurrentHashMap<>();
        this.executions = new ConcurrentHashMap<>();
        this.componentRegistry = new ConcurrentHashMap<>();
        logger.info("Workflow Engine initialized");
    }
    
    /**
     * Register a workflow with the engine
     * @param workflow The workflow to register
     * @return The ID of the registered workflow
     */
    public String registerWorkflow(Workflow workflow) {
        workflows.put(workflow.getId(), workflow);
        logger.info("Registered workflow: " + workflow.getId() + " - " + workflow.getName());
        return workflow.getId();
    }
    
    /**
     * Register a component with available actions
     * @param componentId ID of the component
     * @param actions Map of action names to functions
     */
    public void registerComponent(String componentId, 
                                 Map<String, Function<Map<String, Object>, Map<String, Object>>> actions) {
        componentRegistry.put(componentId, actions);
        logger.info("Registered component: " + componentId + " with actions: " + actions.keySet());
    }
    
    /**
     * Execute a workflow with the given inputs
     * @param workflowId ID of the workflow to execute
     * @param inputs Input data for the workflow
     * @return The workflow execution object
     */
    public WorkflowExecution executeWorkflow(String workflowId, Map<String, Object> inputs) {
        if (!workflows.containsKey(workflowId)) {
            throw new IllegalArgumentException("Workflow not found: " + workflowId);
        }
        
        Workflow workflow = workflows.get(workflowId);
        WorkflowExecution execution = new WorkflowExecution(workflow);
        executions.put(execution.getId(), execution);
        
        logger.info("Starting workflow execution: " + execution.getId() + " for workflow: " + workflowId);
        
        try {
            // Execute each step in sequence
            Map<String, Map<String, Object>> stepResults = new HashMap<>();
            
            for (int i = 0; i < workflow.getSteps().size(); i++) {
                WorkflowStep step = workflow.getSteps().get(i);
                logger.info("Executing step " + (i+1) + "/" + workflow.getSteps().size() + ": " + step.getName());
                
                // If component not registered, skip with error
                if (!componentRegistry.containsKey(step.getComponentId())) {
                    String errorMsg = "Component not registered: " + step.getComponentId();
                    Map<String, Object> error = new HashMap<>();
                    error.put("step", step.getId());
                    error.put("error", errorMsg);
                    execution.getErrors().add(error);
                    logger.severe(errorMsg);
                    continue;
                }
                
                Map<String, Function<Map<String, Object>, Map<String, Object>>> component = 
                    componentRegistry.get(step.getComponentId());
                
                // If action not registered, skip with error
                if (!component.containsKey(step.getAction())) {
                    String errorMsg = "Action not found: " + step.getAction() + " for component: " + step.getComponentId();
                    Map<String, Object> error = new HashMap<>();
                    error.put("step", step.getId());
                    error.put("error", errorMsg);
                    execution.getErrors().add(error);
                    logger.severe(errorMsg);
                    continue;
                }
                
                // Map inputs
                Map<String, Object> stepInputs = new HashMap<>();
                for (Map.Entry<String, String> mapping : step.getInputMapping().entrySet()) {
                    String target = mapping.getKey();
                    String source = mapping.getValue();
                    
                    if (source.startsWith("$.inputs.")) {
                        String inputKey = source.substring("$.inputs.".length());
                        if (inputs.containsKey(inputKey)) {
                            stepInputs.put(target, inputs.get(inputKey));
                        }
                    } else if (source.startsWith("$.steps.")) {
                        String[] parts = source.split("\\.", 4);
                        if (parts.length >= 4) {
                            String sourceStepId = parts[2];
                            String outputKey = parts[3];
                            
                            if (stepResults.containsKey(sourceStepId) && 
                                stepResults.get(sourceStepId).containsKey(outputKey)) {
                                stepInputs.put(target, stepResults.get(sourceStepId).get(outputKey));
                            }
                        }
                    }
                }
                
                // Execute action
                try {
                    Function<Map<String, Object>, Map<String, Object>> actionFunc = component.get(step.getAction());
                    Map<String, Object> result = actionFunc.apply(stepInputs);
                    stepResults.put(step.getId(), result);
                    
                    // Map outputs to workflow results
                    for (Map.Entry<String, String> mapping : step.getOutputMapping().entrySet()) {
                        String target = mapping.getKey();
                        String source = mapping.getValue();
                        
                        if (result.containsKey(source)) {
                            execution.getResults().put(target, result.get(source));
                        }
                    }
                } catch (Exception e) {
                    String errorMsg = "Error executing step " + step.getId() + ": " + e.getMessage();
                    Map<String, Object> error = new HashMap<>();
                    error.put("step", step.getId());
                    error.put("error", errorMsg);
                    execution.getErrors().add(error);
                    logger.log(Level.SEVERE, errorMsg, e);
                }
            }
            
            // Mark execution as complete
            boolean success = execution.getErrors().isEmpty();
            execution.complete(success);
            
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Error executing workflow: " + e.getMessage(), e);
            Map<String, Object> error = new HashMap<>();
            error.put("workflow", workflowId);
            error.put("error", e.getMessage());
            execution.getErrors().add(error);
            execution.complete(false);
        }
        
        return execution;
    }
    
    /**
     * Get the status of a workflow execution
     * @param executionId ID of the execution
     * @return Execution details
     */
    public Map<String, Object> getExecutionStatus(String executionId) {
        if (!executions.containsKey(executionId)) {
            throw new IllegalArgumentException("Execution not found: " + executionId);
        }
        
        WorkflowExecution execution = executions.get(executionId);
        return execution.toMap();
    }
    
    /**
     * Workflow step class
     */
    public static class WorkflowStep {
        private final String id;
        private final String name;
        private final String componentId;
        private final String action;
        private final Map<String, String> inputMapping;
        private final Map<String, String> outputMapping;
        
        /**
         * Create a workflow step
         * @param name Name of the step
         * @param componentId ID of the component to use
         * @param action Action to perform
         * @param inputMapping Mapping of inputs
         * @param outputMapping Mapping of outputs
         */
        public WorkflowStep(String name, String componentId, String action, 
                           Map<String, String> inputMapping, Map<String, String> outputMapping) {
            this.id = UUID.randomUUID().toString();
            this.name = name;
            this.componentId = componentId;
            this.action = action;
            this.inputMapping = inputMapping != null ? inputMapping : new HashMap<>();
            this.outputMapping = outputMapping != null ? outputMapping : new HashMap<>();
        }
        
        public String getId() { return id; }
        public String getName() { return name; }
        public String getComponentId() { return componentId; }
        public String getAction() { return action; }
        public Map<String, String> getInputMapping() { return inputMapping; }
        public Map<String, String> getOutputMapping() { return outputMapping; }
        
        /**
         * Convert to a map representation
         * @return Map representation of the step
         */
        public Map<String, Object> toMap() {
            Map<String, Object> map = new HashMap<>();
            map.put("id", id);
            map.put("name", name);
            map.put("component_id", componentId);
            map.put("action", action);
            map.put("input_mapping", inputMapping);
            map.put("output_mapping", outputMapping);
            return map;
        }
    }
    
    /**
     * Workflow class
     */
    public static class Workflow {
        private final String id;
        private final String name;
        private final String description;
        private final List<WorkflowStep> steps;
        private final LocalDateTime createdAt;
        private LocalDateTime updatedAt;
        private String status;
        
        /**
         * Create a workflow
         * @param name Name of the workflow
         * @param description Description of the workflow
         */
        public Workflow(String name, String description) {
            this.id = UUID.randomUUID().toString();
            this.name = name;
            this.description = description;
            this.steps = new ArrayList<>();
            this.createdAt = LocalDateTime.now();
            this.updatedAt = this.createdAt;
            this.status = "draft";
        }
        
        public String getId() { return id; }
        public String getName() { return name; }
        public String getDescription() { return description; }
        public List<WorkflowStep> getSteps() { return steps; }
        public LocalDateTime getCreatedAt() { return createdAt; }
        public LocalDateTime getUpdatedAt() { return updatedAt; }
        public String getStatus() { return status; }
        
        /**
         * Add a step to the workflow
         * @param step Step to add
         */
        public void addStep(WorkflowStep step) {
            steps.add(step);
            updatedAt = LocalDateTime.now();
        }
        
        /**
         * Convert to a map representation
         * @return Map representation of the workflow
         */
        public Map<String, Object> toMap() {
            Map<String, Object> map = new HashMap<>();
            map.put("id", id);
            map.put("name", name);
            map.put("description", description);
            
            List<Map<String, Object>> stepsList = new ArrayList<>();
            for (WorkflowStep step : steps) {
                stepsList.add(step.toMap());
            }
            map.put("steps", stepsList);
            
            map.put("created_at", createdAt.toString());
            map.put("updated_at", updatedAt.toString());
            map.put("status", status);
            
            return map;
        }
    }
    
    /**
     * Workflow execution class
     */
    public static class WorkflowExecution {
        private final String id;
        private final String workflowId;
        private final Workflow workflow;
        private final LocalDateTime startedAt;
        private LocalDateTime completedAt;
        private String status;
        private final Map<String, Object> results;
        private final List<Map<String, Object>> errors;
        
        /**
         * Create a workflow execution
         * @param workflow Workflow to execute
         */
        public WorkflowExecution(Workflow workflow) {
            this.id = UUID.randomUUID().toString();
            this.workflowId = workflow.getId();
            this.workflow = workflow;
            this.startedAt = LocalDateTime.now();
            this.status = "running";
            this.results = new HashMap<>();
            this.errors = new ArrayList<>();
        }
        
        public String getId() { return id; }
        public String getWorkflowId() { return workflowId; }
        public Workflow getWorkflow() { return workflow; }
        public LocalDateTime getStartedAt() { return startedAt; }
        public LocalDateTime getCompletedAt() { return completedAt; }
        public String getStatus() { return status; }
        public Map<String, Object> getResults() { return results; }
        public List<Map<String, Object>> getErrors() { return errors; }
        
        /**
         * Mark the execution as complete
         * @param success Whether the execution was successful
         */
        public void complete(boolean success) {
            this.completedAt = LocalDateTime.now();
            this.status = success ? "completed" : "failed";
        }
        
        /**
         * Convert to a map representation
         * @return Map representation of the execution
         */
        public Map<String, Object> toMap() {
            Map<String, Object> map = new HashMap<>();
            map.put("id", id);
            map.put("workflow_id", workflowId);
            map.put("started_at", startedAt.toString());
            map.put("completed_at", completedAt != null ? completedAt.toString() : null);
            map.put("status", status);
            map.put("results", results);
            map.put("errors", errors);
            return map;
        }
    }
    
    /**
     * Main method for demonstration
     */
    public static void main(String[] args) {
        // Create workflow engine
        WorkflowEngine engine = new WorkflowEngine();
        
        // Register a sample component
        Map<String, Function<Map<String, Object>, Map<String, Object>>> dataProcessor = new HashMap<>();
        
        // Sample action: parse JSON data
        dataProcessor.put("parse_json", inputs -> {
            Map<String, Object> result = new HashMap<>();
            String jsonData = (String) inputs.get("json_data");
            // In a real implementation, this would parse the JSON
            result.put("result", "Parsed " + jsonData);
            return result;
        });
        
        engine.registerComponent("data_processor", dataProcessor);
        
        // Create a sample workflow
        Workflow workflow = new Workflow("Sample Workflow", "Demonstration workflow");
        
        // Add a step
        Map<String, String> inputMapping = new HashMap<>();
        inputMapping.put("json_data", "$.inputs.data");
        
        Map<String, String> outputMapping = new HashMap<>();
        outputMapping.put("parsed_result", "result");
        
        WorkflowStep step = new WorkflowStep(
            "Parse Data", 
            "data_processor", 
            "parse_json", 
            inputMapping, 
            outputMapping
        );
        
        workflow.addStep(step);
        
        // Register the workflow
        engine.registerWorkflow(workflow);
        
        // Execute the workflow with sample input
        Map<String, Object> inputs = new HashMap<>();
        inputs.put("data", "{\"key\": \"value\"}");
        
        WorkflowExecution execution = engine.executeWorkflow(workflow.getId(), inputs);
        
        // Print execution results
        System.out.println("Execution ID: " + execution.getId());
        System.out.println("Status: " + execution.getStatus());
        System.out.println("Results: " + execution.getResults());
    }
}