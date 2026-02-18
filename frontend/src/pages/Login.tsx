import React, { useState } from "react"
import axios from "axios"

export default function Login() {

  const [username,setUsername]=useState("")
  const [password,setPassword]=useState("")

 const login = async () => {

  const res = await axios.post(
    `http://192.168.10.216:9200/auth/login?username=${username}&password=${password}`
  )

  localStorage.setItem("token", res.data.access_token)

  window.location.href="/dashboard"
}



  return (
    <div style={{padding:40}}>
      <h2>Optical POS Login</h2>

      <input
        placeholder="Username"
        onChange={e=>setUsername(e.target.value)}
      />

      <br/><br/>

      <input
        type="password"
        placeholder="Password"
        onChange={e=>setPassword(e.target.value)}
      />

      <br/><br/>

      <button onClick={login}>
        Login
      </button>
    </div>
  )
}
