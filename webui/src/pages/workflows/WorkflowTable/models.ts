export interface Task {
  name: string;
  arguments: Map<string, string>;
  received_date: string;
  parent_task_id?: string;
  workflow_id: string;
  task_id: string;
  node_names: string[];
  tags?: string[];
  reject_counter: number;
  planned_date?: string;
  status?: string;
}

export interface TaskStatus {
  task_id: string;
  status: string;
}

export interface WorkflowStatus {
  status: string;
  tasks: Array<TaskStatus>;
  workflow_id: string;
};

export interface ListItemType {
  workflowId: string;
  namespace: string;
  status: string;
  tags: string;
  entryTask: string;
  createdDate: string;
  key: string;
}

export interface PagedListItemType {
  items: Array<ListItemType>;
  totalCount: number;
}

export interface PagedTaskLogs {
  total_count: number;
  log_lines: Array<string>;
}

export interface WorkflowData {
  workflow_id: string;
  namespace: string;
  tags: string[];
}

export interface Workflow {
  created_date: string;
  entry_task: Task;
  status: string;
  workflow: WorkflowData;
}

export interface PagedWorkflowTasks {
  total_count: number;
  tasks: Array<Task>;
  count: number;
}

export interface PagedWorkflows {
  total_count: number;
  workflows: Array<Workflow>;
  count: number;
}

export interface HandleWorkflowResponse {
  status: string;
}

export interface WorkflowMetrics {
  workflow_id: string;
  namespace: string;
  status: string;
  created_date: string;
}