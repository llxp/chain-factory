import { PagedListItemType, PagedWorkflows } from './models';

const userLang = navigator.language;

var options: Intl.DateTimeFormatOptions = {
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "numeric",
  minute: "numeric",
  second: "numeric"
};

export function workflowsToListItemType(workflows: PagedWorkflows): PagedListItemType {
  return {
    items: workflows?.workflows.map(workflow => {
      const entryTask = workflow.entry_task ? workflow.entry_task.name : "";
      const tags = workflow.workflow.tags.join(', ') || "";
      const workflowStatus = workflow.status;
      const createdDate = workflow.created_date ? new Date(workflow.created_date).toLocaleString(userLang, options) : "";
      const workflowId = workflow.workflow.workflow_id;
      const namespace = workflow.workflow.namespace;
      return {
        workflowId: workflowId,
        namespace: namespace,
        tags: tags,
        status: workflowStatus,
        entryTask: entryTask,
        createdDate: createdDate,
        key: workflowId + namespace
      };
    }),
    totalCount: workflows?.total_count
  };
}

export function getbackgroundColor(status) {
  switch(status?.toLowerCase()) {
    case 'task':
    case 'none':
      return '#00aa00';
    case 'exception':
    case 'timeout':
    case 'false':
    case 'aborted':
    case 'stopped':
      return '#aa0000';
    case 'running':
      return '#FFFF00';
  }
}

export function scrollToTop() {
  window.scrollTo(0, 0);
}

export function scrollToBottom(ref: HTMLUListElement) {
  const scrollHeight = ref.scrollHeight;
  const height = ref.clientHeight;
  const maxScrollTop = scrollHeight - height;
  ref.scrollTo({top: maxScrollTop, left: 0, behavior: "smooth"});
}