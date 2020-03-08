let api = new Api()
const submit = document.querySelector('#submit-btn')
let isSubmitting = false
submit.addEventListener('click', submitFn)
async function submitFn() {
    if (isSubmitting) return
    isSubmitting = true
    const email = document.querySelector('#email').value
    const pw = document.querySelector('#password').value
    try {
        let user = await api.post('/login', { email: email })
        console.log(user)
        // submit.value = 'Signing in...'
        document.querySelector('.login-box').innerHTML = `
        <img style="transform: translate(-25%, 10%)" src="loader.gif"></img>
        <h1>Please wait while we load your credentials...</h1>`
        submitSuccess(user)
    } catch (e) {
        console.log(e)
        submitFail()
    }
}

function submitSuccess(auth) {
    chrome.storage.sync.set({ auth: auth })
    window.close()
}

function submitFail() {
    submit.value = 'Sign in'
    isSubmitting = false
    Snackbar.show({
        text: 'Incorrect credentials',
        showAction: false,
        pos: 'bottom-center'
    })
}

