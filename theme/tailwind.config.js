// filepath: c:\Users\matia\SportFit\theme\tailwind.config.js
module.exports = {
    content: [
        '../templates/**/*.html', // Plantillas en la carpeta theme/templates
        '../../**/templates/**/*.html', // Plantillas en otras aplicaciones
    ],
    theme: {
        extend: {},
    },
    plugins: [],
};