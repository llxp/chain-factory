"""
wait_time ==>       Time to wait after a task has been
                    rejected/rescheduled/sent to another blocked/waiting queue
prefetch_count ==>  Global setting to control the QoS in the amqp library,
                    it specifies how many messages whould be prefetched
                    from the server.
worker_count ==>    Amount of worker threads to spawn.
                    Later there can be configured spcific blocklists
                    of functions to only run e.g. on nodes,
                    which have more threads for smaller tasks
"""
from os import getenv


# seconds to wait between each queue fetch
wait_time = int(getenv("WAIT_TIME", 60))
# how many tasks should be prefetched by amqp library
prefetch_count = int(getenv("PREFETCH_COUNT", 1))
# number of threads to listen on the queue
worker_count = int(getenv("WORKER_COUNT", 1))
# when should a waiting task be put back to the main/task queue (in seconds)
max_task_age_wait_queue: int = int(getenv("MAX_TASK_AGE_WAIT_QUEUE", 60))
# if sticky_tasks option is set,
# # only execute the full workflow on the node it started on
sticky_tasks = getenv("STICKY_TASKS", False)
# number of times a task can be rejected,
# until it will be put on the wait queue
reject_limit = int(getenv("REJECT_LIMIT", 10))
# performs a check, if the current node name already exists
# throws an exception, if this option is set and the current node name
# is already registered
unique_hostnames = getenv("UNIQUE_HOSTNAMES", False)
# override an existing node registration
force_register = getenv("FORCE_REGISTER", True)
# can be used to suppress all stdout output
task_log_to_stdout = getenv("TASK_LOG_TO_STDOUT", True)
# can be used to suppress all external logging
task_log_to_external = getenv("TASK_LOG_TO_EXTERNAL", True)
# redis key to mark a workflow as finished, if an entry is found in this list
workflow_status_redis_key = getenv(
    "WORKFLOW_STATUS_REDIS_KEY", "workflow_status")
# redis key to mark a task as finished, if an entry is found in this list
task_status_redis_key = getenv("TASK_STATUS_REDIS_KEY", "task_status")
# heartbeat configuration
# redis key, which should be updated
heartbeat_redis_key = getenv("HEARTBEAT_REDIS_KEY", "heartbeat")
# wait time between each update (in seocnds)
heartbeat_sleep_time: int = int(getenv("HEARTBEAT_SLEEP_TIME", 1))
# redis key, which should hold the block list for the normal block list
incoming_block_list_redis_key = getenv(
    "INCOMING_BLOCK_LIST_REDIS_KEY", "incoming_block_list")
# redis key, which should hold the block list for the wait block list
wait_block_list_redis_key = getenv(
    "WAIT_BLOCK_LIST_REDIS_KEY", "wait_block_list")
# task control channel redis key
task_control_channel_redis_key = getenv(
    "TASK_CONTROL_CHANNEL_REDIS_KEY", "task_control_channel")
# node control channel redis key
node_control_channel_redis_key = getenv(
    "NODE_CONTROL_CHANNEL_REDIS_KEY", "node_control_channel")
task_queue = getenv("TASK_QUEUE", "it_queue")
wait_queue = getenv("WAIT_QUEUE", "iw_queue")
incoming_blocked_queue = getenv(
    "INCOMING_BLOCKED_QUEUE", "ib_queue")
wait_blocked_queue = getenv("WAIT_BLOCKED_QUEUE", "wb_queue")
namespace = getenv("NAMESPACE", "test01")
namespace_key = getenv("NAMESPACE_KEY", "")
# maximum time in seconds a task can run, until it will be aborted
task_timeout = getenv("TASK_TIMEOUT", None)
task_repeat_on_timeout = getenv("TASK_REPEAT_ON_TIMEOUT", False)
