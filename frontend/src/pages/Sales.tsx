import React, { useEffect, useState, useRef } from "react"
import axios from "axios"

const API = "http://192.168.10.216:9200"

export default function Sales(){

  const token = localStorage.getItem("token")

  const headers = {
    Authorization:`Bearer ${token}`
  }

  const scanRef = useRef<HTMLInputElement>(null)

  const [items,setItems] = useState<any[]>([])
  const [scan,setScan] = useState("")
  const [cart,setCart] = useState<any[]>([])

  const [custName,setCustName]=useState("")
  const [custPhone,setCustPhone]=useState("")
  const [payment,setPayment]=useState("CASH")
  const [paid,setPaid]=useState("")

  // ================= LOAD ITEMS =================
  useEffect(()=>{
    axios.get(`${API}/items/`,{headers})
      .then(res=>setItems(res.data))
      .catch(()=>alert("Auth expired — login again"))
  },[])

  // ================= SCAN =================
  const handleScan=(e:any)=>{
    if(e.key !== "Enter") return

    const term = scan.toLowerCase()

    const found = items.find(i =>
      (i.barcode && i.barcode.toLowerCase() === term) ||
      i.name.toLowerCase().includes(term) ||
      (i.model && i.model.toLowerCase().includes(term))
    )

    if(found){
      addToCart(found)
      setScan("")
    } else {
      alert("Item not found")
    }
  }

  // ================= ADD =================
  const addToCart=(item:any)=>{

    if(item.stock_qty <= 0){
      alert("Out of stock")
      return
    }

    const exist = cart.find(c=>c.id===item.id)

    if(exist){
      if(exist.qty + 1 > item.stock_qty){
        alert("Stock limit reached")
        return
      }

      setCart(cart.map(c =>
        c.id===item.id ? {...c,qty:c.qty+1}:c
      ))
    }
    else{
      setCart([...cart,{
        id:item.id,
        name:item.name,
        price:Number(item.selling_price),
        gst:Number(item.gst_percent || 0),
        qty:1,
        stock:item.stock_qty
      }])
    }
  }

  // ================= QTY =================
  const changeQty=(id:number,q:number)=>{
    setCart(cart.map(c=>{
      if(c.id!==id) return c
      if(q<=0 || q>c.stock) return c
      return {...c,qty:q}
    }))
  }

  // ================= REMOVE =================
  const remove=(id:number)=>{
    setCart(cart.filter(c=>c.id!==id))
  }

  // ================= TOTALS =================
  const taxable = cart.reduce((s,c)=>s+c.price*c.qty,0)
  const gst = cart.reduce((s,c)=>s+(c.price*c.qty*c.gst/100),0)
  const grand = taxable + gst
  const balance = grand - Number(paid || 0)

  // ================= PDF PRINT =================
  const printInvoice = async (saleId:number)=>{
    const res = await axios.get(
      `${API}/sales/${saleId}/pdf`,
      {
        headers,
        responseType:"blob"
      }
    )

    const file = new Blob([res.data],{type:"application/pdf"})
    const url = URL.createObjectURL(file)
    window.open(url)
  }

  // ================= SUBMIT =================
  const submit = async()=>{

  if(cart.length===0){
    alert("Cart empty")
    return
  }

  try{

    const payload = {

      customer_name: custName || null,
      customer_phone: custPhone || null,

      items: cart.map(c=>({
        item_id: Number(c.id),
        qty: Number(c.qty),
        price: Number(c.price)
      })),

      payment_amount: Number(paid || grand),
      payment_mode: payment
    }

    console.log("SALE PAYLOAD:", payload)

    const res = await axios.post(
      `${API}/sales/`,
      payload,
      {headers}
    )

    const saleId = res.data.id ?? res.data.sale_id

    await printInvoice(saleId)

    setCart([])

  }catch(err:any){

    console.error(err.response?.data)

    alert(
      err.response?.data?.detail ||
      "Sale failed"
    )
  }
}


  // ================= SHORTCUTS =================
  useEffect(()=>{
    const keys=(e:any)=>{
      if(e.key==="Delete") setCart(c=>c.slice(0,-1))
      if(e.key==="Escape") setCart([])
      if(e.key==="F2") submit()
    }
    window.addEventListener("keydown",keys)
    return ()=>window.removeEventListener("keydown",keys)
  },[cart])

  // ================= UI =================
  return(
    <div style={{padding:30}}>

      <h1>Sales Billing</h1>

      <input
        ref={scanRef}
        autoFocus
        placeholder="Scan or type → Enter"
        value={scan}
        onChange={e=>setScan(e.target.value)}
        onKeyDown={handleScan}
        style={{width:"100%",fontSize:20,padding:10}}
      />

      <div style={{marginTop:10}}>
        <input placeholder="Customer"
          value={custName}
          onChange={e=>setCustName(e.target.value)}
        />

        <input placeholder="Phone"
          value={custPhone}
          onChange={e=>setCustPhone(e.target.value)}
        />
      </div>

      <table border={1} cellPadding={6} style={{marginTop:20,width:"100%"}}>
        <thead>
          <tr>
            <th>Item</th>
            <th>Qty</th>
            <th>Rate</th>
            <th>GST%</th>
            <th>Total</th>
            <th></th>
          </tr>
        </thead>

        <tbody>
          {cart.map(c=>(
            <tr key={c.id}>
              <td>{c.name}</td>

              <td>
                <input type="number"
                  value={c.qty}
                  onChange={e=>changeQty(c.id,Number(e.target.value))}
                />
              </td>

              <td>{c.price}</td>
              <td>{c.gst}</td>

              <td>
                {(c.price*c.qty*(1+c.gst/100)).toFixed(2)}
              </td>

              <td>
                <button onClick={()=>remove(c.id)}>X</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Taxable ₹ {taxable.toFixed(2)}</h3>
      <h3>GST ₹ {gst.toFixed(2)}</h3>
      <h2>Grand ₹ {grand.toFixed(2)}</h2>

      <div>
        <select value={payment}
          onChange={e=>setPayment(e.target.value)}
        >
          <option>CASH</option>
          <option>UPI</option>
          <option>CARD</option>
        </select>

        <input
          placeholder="Paid"
          value={paid}
          onChange={e=>setPaid(e.target.value)}
        />
      </div>

      <h3>Balance ₹ {balance.toFixed(2)}</h3>

      <button onClick={submit}>
        Complete Sale (F2)
      </button>

    </div>
  )
}
