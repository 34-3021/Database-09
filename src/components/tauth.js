import { BACKEND_BASE_URL, WEBSOCKET_URL } from "./endpoints.js";
export const getTAuthStatus = () => {
    return new Promise((resolve, reject) => {
        fetch("https://account.tmysam.top/apis/sso-interface.php", {
            credentials: "include",
        })
            .then((res) => res.json())
            .then((res) => {
                if (res.status === 0) {
                    resolve({
                        status: true,
                        message: "已确认登录状态",
                    });
                } else {
                    resolve({
                        status: false,
                        message: "未登录或邮件未验证",
                    });
                }
            })
            .catch((error) => {
                reject(error);
            });
    });
};

export const genTAuthToken = () => {
    return new Promise((resolve, reject) => {
        fetch(
            "https://account.tmysam.top/apis/thirdparty_token_gen.php?app=InfiniDoc",
            {
                credentials: "include",
            }
        )
            .then((res) => res.json())
            .then((res) => {
                if (res.success) {
                    resolve({
                        status: true,
                        token: res.token,
                        message: "已生成 TAuth Token",
                    });
                } else {
                    resolve({
                        status: false,
                        message:
                            "生成 TAuth Token 失败。服务器反馈：" + res.error,
                    });
                }
            })
            .catch((error) => {
                reject(error);
            });
    });
};

export const loginWithTauthGetToken = (token) => {
    // http://local.tmysam.top:8001/login/tauth?token=tauth_token

    return new Promise((resolve, reject) => {
        fetch(BACKEND_BASE_URL + `/login/tauth`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ token }),
        })
            .then((res) => res.json())
            .then((res) => {
                if (res.success) {
                    resolve({
                        status: true,
                        token: res.token,
                    });
                } else {
                    resolve({
                        status: false,
                        token: res.token,
                    });
                }
            })
            .catch((error) => {
                reject(error);
            });
    });
};

const validateUsername = (username) => {
    return /^[a-zA-Z0-9_-]{4,32}$/.test(username);
};

const sha256 = async (str) => {
    const encoder = new TextEncoder();
    const data = encoder.encode(str);
    const hash = await crypto.subtle.digest("SHA-256", data);
    let result = "";
    const view = new DataView(hash);
    for (let i = 0; i < hash.byteLength; i += 4) {
        result += ("00000000" + view.getUint32(i).toString(16)).slice(-8);
    }
    return result;
};

export const loginTAuth = async () => {
    let res = await getTAuthStatus();
    if (!res.status) {
        return {
            status: false,
            message: "未登录或邮件未验证",
        };
    }
    let res2 = await genTAuthToken();
    if (!res2.status) {
        return {
            status: false,
            message: "生成 TAuth Token 失败",
        };
    }
    let res3 = await loginWithTauthGetToken(res2.token);
    if (!res3.status) {
        return {
            status: false,
            message: "登录失败",
        };
    }
    return {
        status: true,
        message: "登录成功",
        token: res3.token,
    };
};

export const loginNative = async (username, password) => {
    if (!validateUsername(username)) {
        return {
            status: false,
            message: "用户名格式错误",
        };
    }
    let passwordHash = await sha256(password);
    let res = await fetch(BACKEND_BASE_URL + `/login/native`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password: passwordHash }),
    });

    let resj = await res.json();
    if (!resj.success) {
        return {
            status: false,
            message: "登录失败：" + resj.error_message,
        };
    }

    return {
        status: true,
        message: "登录成功",
        token: resj.token,
    };
};

export const registerNative = async (username, password) => {
    if (!validateUsername(username)) {
        return {
            status: false,
            message: "用户名格式错误",
        };
    }
    let passwordHash = await sha256(password);
    let res = await fetch(BACKEND_BASE_URL + `/register/native`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password: passwordHash }),
    });
    let resj = await res.json();
    if (!resj.success) {
        return {
            status: false,
            message: "注册失败：" + resj.error_message,
        };
    }

    return {
        status: true,
        message: "注册成功",
        token: resj.token,
    };
};
