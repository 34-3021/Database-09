import uvicorn

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True,
                ssl_keyfile="./cert/local.tmysam.top-key.pem", ssl_certfile="./cert/local.tmysam.top.pem")
