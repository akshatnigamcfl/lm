async function ftN(link, method, headers, body){
    // console.log('link', link)
    let a
    if (body !== ''){
        a = await fetch(link, {'method': method, headers: headers, body: body})
    } else{
        a = await fetch(link, {'method': method, headers: headers})
    }

    if (a.status !== 204 ){
        a = await a.json()
    } else {
        a = { "status": 204, "message": 'no data', 'data': []}
    }
    
    return a
}