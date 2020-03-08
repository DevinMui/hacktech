class Api {
    constructor(url = 'https://hacktech-ebay.appspot.com') {
        this.url = url
        this.options = {
            mode: 'cors',
            headers: { 'Content-Type': 'application/json' }
        }
    }

    async get(uri, queries = []) {
        var query = ''
        if (queries.length) {
            url += '?'
            query = queries.join('&')
        }
        var options = this.options
        options.method = 'GET'
        return await fetch(this.url + uri + query, options)
    }

    async post(uri, body = {}) {
        var options = this.options
        options.method = 'POST'
        options.body = JSON.stringify(body)
        return await fetch(this.url + uri, options)
    }
}
