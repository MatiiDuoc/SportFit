// Guardar CSRF token de la cookie
if (pm.cookies.get('csrftoken')) {
    pm.environment.set('csrftoken', pm.cookies.get('csrftoken'));
}
// Guardar token de autenticación si viene en JSON
try {
    let json = pm.response.json();
    if (json.token) {
        pm.environment.set('token', json.token);
    }
} catch(e) {}