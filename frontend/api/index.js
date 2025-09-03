class API {
    constructor(base_url = "/v1") {
        this.base_url = base_url;
    }

    /**
     * 
     * @param {string} path 
     */
    #getUrl(path) {
        if(path.startsWith("/")) {
            return this.base_url + path;
        }
        return [this.base_url, path].join("/");
    }

    /**
     * 
     * @param {FetchRequest} request 
     */
    async #request(request) {
        const path = this.#getUrl(request.path);
        const response = await fetch(path, {
            method: request.method,
            headers: request.headers,
            body: request.body
        });
        if(!response.ok) {
            throw await response.text();
        }
        return await response.json();
    }

    async #post(path, body) {
        const request = new FetchRequest({
            path, body, method: "POST",
            headers: new Headers({ 'content-type': 'application/json' }),
        });
        return this.#request(request);
    }

    compliance = {
        post: (body) => this.#post("/compliance", body),
    }
}

class FetchRequest {
    #body
    constructor({ path, headers = new Headers(), body, method }) {
        this.path = path;
        this.headers = headers
        this.#body = body
        this.method = method
    }

    get body() {
        return JSON.stringify(this.#body);
    }
}