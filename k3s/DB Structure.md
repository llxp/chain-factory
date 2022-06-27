# DB Structure

# DBs:
# main database: orchestrator_db
## collections:
- idp_domain_config
  ```{
    _id: ObjectId(),
    client_cert_config: {
        cert: 'base64 encoded cert of client certificate used for the authentication api, needed if mtls is enabled for the authentication api',
        key: 'base64 encoded key of client certificate used for the authentication api, needed if mtls is enabled for the authentication api'
    },
    created: ISODate(),
    domain: 'domain.com',
    enabled: true,
    endpoints: {
        user_information_endpoint: 'https://authentication-api-endpoint.fqdn/user_information',
        translate_users_endpoint: 'https://authentication-api-endpoint.fqdn/translate_users'
    },
    updated: ISODate()
  }
  ````
- idp_role_config
  ```
  {
    _id: ObjectId(),
    enabled: true,
    created: ISODate(),
    updated: ISODate(),
    auth_config: [
        {
            name: 'cn=Administrators,ou=Users,dc=ad,dc=com',
            auth_type: 'GROUP'
        }
    ],
    role: 'PLATFORM_ADMINISTRATOR',
    domain: 'domain.com',
    scopes: [
        'auth',
        'user',
        'node_admin',
        'workflow_controller'
    ]
  }
  ```
- namespaces
  # Auto generated through api, (POST /api/v1/credentials)
  ```
  {
    _id: ObjectId(),
    allowed_users: [
        'username@domain.com'
    ],
    domain: 'domain.com',
    enabled: true,
    namespace: 'test01'
  }
  ```
- refresh_token
  ```
  {
    _id: ObjectId(),
    created_at: int,
    expires_at: int,
    jti: 'serial number of jwe refresh token',
    revoked: false,
    scopes: [
        'auth'  # requested scope during login
    ],
    username: 'username@domain.com'
  }
  ```
- management_credentials
  ```
  {
    _id: ObjectId(),
    credentials: 'encrypted credentials',
    domain: 'jumpcloud.com',
    namespace: 'test02'
  }
  ```
## namespace specific database (one per namespace)
## naming scheme: `<namespace>_<lowercase domain>`
## collections:
- logs
  ```
  {
    _id: ObjectId(),
    log_line: 'log line',
    task_id: 'task id',
    workflow_id: 'workflow id'
  }
  ```
- node_tasks
  ```
  {
    _id: ObjectId(),
    namespace: 'namespace',
    node_name: 'node name',
    tasks: [
        {
            name: 'task name',
            arguments: {
              arg1: 'arg1',
              arg2: 'arg2'
            }
        }
    ]
  }
  ```
- task_status
  ```
  {
    _id: ObjectId(),
    created_date: 'yyyy-mm-ddThh:mm:ss.z',
    namespace: 'namespace',
    status: 'None',  # None, Exception, Task, Stopped
    task_id: '8ac68970-d758-11ec-8bde-faffc2426d3b-4e15c7f2-726a-46c0-ba08-8a08f9b68955'
  }
  ```
- task_workflow_association
  ```
  {
    _id: ObjectId(),
    node_name: 'node name',
    task: {
        name: 'task_name',
        arguments: {
          arg1: 'arg1',
          arg2: 'arg2'
        },
        received_date: ISODate(),
        parent_task_id: '',
        workflow_id: 'workflow id',
        task_id: 'task id',
        node_names: [],
        tags: [],
        reject_counter: 0,
        planned_date: ISODate()
    },
    workflow_id: 'workflow id'
  }
  ```
- workflow
  ```
  {
    _id: ObjectId(),
    created_date: ISODate(),
    namespace: 'namespace',
    node_name: 'node name',
    tags: ['tag01', 'tag02'],
    workflow_id: 'workflow id',
  }
  ```
- workflow_status
  ```
  {
    _id: ObjectId(),
    created_date: ISODate(),
    namespace: 'namespace',
    status: 'None',  # None, Exception
    workflow_id: 'workflow id'
  }
  ```