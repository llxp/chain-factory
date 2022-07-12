export interface HttpOptions {
  baseURL?: string
  transformRequest?: { (request: JsonObject): JsonObject }[]
  transformResponse?: { <T>(response: HttpResponse<T>): HttpResponse<T> }[]
  headers?: HeadersInit
}

export interface HttpResponse<T> extends Response {
  parsedBody?: T
}

export interface JsonObject {
  [k: string]: any
}

export class Fitch {
  private readonly baseURL: string = ''
  private readonly transformRequest: { (request: JsonObject): JsonObject }[] = []
  private readonly transformResponse: { <T>(request: HttpResponse<T>): HttpResponse<T> }[] = []
  private readonly headers: HeadersInit = {};

  constructor(options?: HttpOptions) {
    if (options && Object.keys(options).length > 0) {
      this.baseURL = options.baseURL || ''
      this.transformRequest = options.transformRequest || []
      this.transformResponse = options.transformResponse || []
      this.headers = { Accept: 'application/json', 'Content-Type': 'application/json', ...options.headers }
    }
  }

  private async http<T>(path: string, args: JsonObject): Promise<T> {
    path = this.baseURL.concat(path)

    return new Promise((resolve, reject) => {
      let response: HttpResponse<T>

      args.headers = { ...this.headers }

      this.transformRequest.forEach((transformer) => {
        args = transformer(args)
      })

      const requestArgs: RequestInit = {
        method: args.method,
        body: JSON.stringify(args.body) || null,
        headers: args.headers
      }
      requestArgs.credentials = 'include'
      const request = new Request(path, requestArgs)

      fetch(request)
        .then((res) => {
          response = res

          return res.text()
        })
        .then((text) => {
          if (response.ok) {
            let body
            try {
              body = text ? JSON.parse(text) : {}
            } catch (e) {
              body = {}
            }
            response.parsedBody = body
            this.transformResponse.forEach((transformer) => {
              response = transformer(response)
            })
            resolve(response.parsedBody)
          } else {
            reject(response)
          }
        })
        .catch((err) => {
          reject(err)
        })
    })
  }

  public async get<T>(path: string): Promise<T> {
    return this.http<T>(path, { method: 'GET' })
  }

  public async delete<T>(path: string): Promise<T> {
    return this.http<T>(path, { method: 'DELETE' })
  }

  public async post<T>(path: string, body: any): Promise<T> {
    return this.http<T>(path, { method: 'POST', body: body })
  }

  public async put<T>(path: string, body: any): Promise<T> {
    return this.http<T>(path, { method: 'PUT', body: body })
  }

  public async patch<T>(path: string, body: any): Promise<T> {
    return this.http<T>(path, { method: 'PATCH', body: body })
  }
}