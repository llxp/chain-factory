export interface ListItemType {
  name: string;
  arguments: Map<string, string>;
  nodeNames: string[];
  task: RegisteredTask;
  namespace: string;
}

export interface RegisteredTask {
  name: string;
  arguments: Map<string, string>;
}

export interface NodeTasks {
  node_name: string;
  namespace: string;
  tasks: RegisteredTask;
}

export interface TaskNodes {
  task: RegisteredTask;
  nodeNames: string[];
  namespace: string;
}

export interface PagedNodeTasks {
  total_count: number;
  node_tasks: Array<NodeTasks>;
}

export interface PagedTaskNodes {
  totalCount: number;
  taskNodes: Array<TaskNodes>;
}

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
}

export interface PagedListItemType {
  totalCount: number;
  items: Array<ListItemType>;
}