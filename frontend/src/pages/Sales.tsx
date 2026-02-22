import React, { useEffect, useState, useRef, useCallback } from "react"
import axios from "axios"

const API = "http://192.168.10.216:9200"

export default function Sales(){

  const token = localStorage.getItem("token")

  const headers = {
    Authorization:`Bearer ${token}`
  }

  const scanRef = useRef<HTMLInputElement>(null)
  const autocompleteRef = useRef<HTMLDivElement>(null)

  const [items,setItems] = useState<any[]>([])
  const [scan,setScan] = useState("")
  const [cart,setCart] = useState<any[]>([])

  const [itemSearch, setItemSearch] = useState("")
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [searchLoading, setSearchLoading] = useState(false)

  const [custName,setCustName]=useState("")
  const [custPhone,setCustPhone]=useState("")
  const [advanceAmount, setAdvanceAmount] = useState("")
  const [advancePaymentMode, setAdvancePaymentMode] = useState("CASH")

  // ================= LOAD ITEMS (for barcode scan fallback) =================
  useEffect(()=>{
    axios.get(`${API}/items/`,{headers})
      .then(res=>setItems(res.data))
      .catch(()=>alert("Auth expired — login again"))
  },[])

  // ================= ITEM SEARCH AUTOCOMPLETE =================
  const fetchSearchResults = useCallback(async (q: string) => {
    if (!q || q.length < 2) {
      setSearchResults([])
      return
    }
    setSearchLoading(true)
    try {
      const res = await axios.get(`${API}/items/search`, { headers, params: { q } })
      setSearchResults(res.data)
      setShowDropdown(true)
    } catch {
      setSearchResults([])
    } finally {
      setSearchLoading(false)
    }
  }, [])

  useEffect(() => {
    const t = setTimeout(() => fetchSearchResults(itemSearch), 250)
    return () => clearTimeout(t)
  }, [itemSearch, fetchSearchResults])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (autocompleteRef.current && !autocompleteRef.current.contains(e.target as Node)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const selectItem = (item: any) => {
    addToCart({
      id: item.id,
      name: item.name,
      selling_price: item.selling_price,
      gst_percent: item.gst_percent ?? 0,
      stock_qty: item.stock_qty
    })
    setItemSearch("")
    setSearchResults([])
    setShowDropdown(false)
  }

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
  const advance = Number(advanceAmount || 0)
  const balance = Math.max(0, grand - advance)

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

    const adv = Number(advanceAmount || 0)

    const payload = {
      customer_name: custName || null,
      customer_phone: custPhone || null,
      items: cart.map(c=>({
        item_id: Number(c.id),
        qty: Number(c.qty),
        price: Number(c.price)
      })),
      advance_amount: adv,
      advance_payment_mode: advancePaymentMode,
      payment_amount: adv,
      payment_method: advancePaymentMode,
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

      {/* Item autocomplete */}
      <div ref={autocompleteRef} style={{ position: "relative", marginBottom: 8 }}>
        <input
          placeholder="Search item (min 2 chars)..."
          value={itemSearch}
          onChange={e => setItemSearch(e.target.value)}
          onFocus={() => searchResults.length > 0 && setShowDropdown(true)}
          style={{ width: "100%", fontSize: 16, padding: 10 }}
        />
        {showDropdown && (itemSearch.length >= 2 || searchResults.length > 0) && (
          <div
            style={{
              position: "absolute",
              top: "100%",
              left: 0,
              right: 0,
              background: "white",
              border: "1px solid #ccc",
              borderRadius: 4,
              maxHeight: 240,
              overflowY: "auto",
              zIndex: 1000,
              boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
            }}
          >
            {searchLoading ? (
              <div style={{ padding: 12, color: "#666" }}>Loading...</div>
            ) : searchResults.length === 0 ? (
              <div style={{ padding: 12, color: "#666" }}>No items found</div>
            ) : (
              searchResults.map((item) => (
                <div
                  key={item.id}
                  onClick={() => selectItem(item)}
                  style={{
                    padding: "10px 12px",
                    cursor: "pointer",
                    borderBottom: "1px solid #eee",
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.background = "#f5f5f5"
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.background = "white"
                  }}
                >
                  {item.name} (Stock: {item.stock_qty})
                </div>
              ))
            )}
          </div>
        )}
      </div>

      <input
        ref={scanRef}
        placeholder="Or scan barcode → Enter"
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
      <h2>Total: ₹ {grand.toFixed(2)}</h2>

      <div style={{ marginTop: 16, padding: 12, background: "#f8f9fa", borderRadius: 6 }}>
        <strong>Advance</strong>
        <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 8, flexWrap: "wrap" }}>
          <input
            type="number"
            placeholder="Advance Amount"
            value={advanceAmount}
            onChange={e=>setAdvanceAmount(e.target.value)}
            min={0}
            step={0.01}
            style={{ width: 140, padding: 8 }}
          />
          <select
            value={advancePaymentMode}
            onChange={e=>setAdvancePaymentMode(e.target.value)}
            style={{ padding: 8 }}
          >
            <option>CASH</option>
            <option>UPI</option>
            <option>CARD</option>
            <option>BANK TRANSFER</option>
          </select>
        </div>
        <div style={{ marginTop: 12, fontSize: 15 }}>
          <span>Total: ₹ {grand.toFixed(2)}</span>
          <span style={{ marginLeft: 16 }}>Advance: ₹ {advance.toFixed(2)}</span>
          <span style={{ marginLeft: 16 }}>Balance: ₹ {balance.toFixed(2)}</span>
        </div>
      </div>

      <button onClick={submit}>
        Complete Sale (F2)
      </button>

    </div>
  )
}
