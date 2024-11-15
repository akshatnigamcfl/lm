function getCookies() {
    const cookies = document.cookie.split(';');
    const cookieObject = {};
    cookies.forEach(cookie => {
        const [key, value] = cookie.split('=').map(c => c.trim());
        cookieObject[key] = decodeURIComponent(value);
    });
    return cookieObject;
}