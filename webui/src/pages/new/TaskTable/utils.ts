import { ListItemType, PagedListItemType, PagedNodeTasks, PagedTaskNodes, RegisteredTask, TaskNodes } from './models';

export function taskToListItemType(task: RegisteredTask, nodeNames: string[], namespace: string): ListItemType {
  return {
    name: task.name,
    arguments: task.arguments,
    nodeNames: nodeNames,
    task: task,
    namespace: namespace
  };
}

export function tasksToListItemTypes(tasks: PagedTaskNodes): PagedListItemType {
  return {
    items: tasks.taskNodes.map(task => taskToListItemType(task.task, task.nodeNames, task.namespace)),
    totalCount: tasks.totalCount
  };
}

export function nodeTasksToTaskNodes(nodeTasks: PagedNodeTasks): PagedTaskNodes {
  const taskNodes: Array<TaskNodes> = [];
  for (const tasks of nodeTasks.node_tasks) {
    const result = taskNodes.find(element => element.task.name === tasks.tasks.name && element.namespace === tasks.namespace);
    if (result) {
      result.nodeNames.push(tasks.node_name);
    } else {
      taskNodes.push({ task: tasks.tasks, nodeNames: [tasks.node_name], namespace: tasks.namespace });
    }
  }
  return {taskNodes: taskNodes, totalCount: nodeTasks?.total_count};
}