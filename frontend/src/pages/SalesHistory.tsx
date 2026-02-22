import React,{useEffect,useState} from "react"
import axios from "axios"

const API="http://192.168.10.216:9200"

export default function SalesHistory(){

  const token=localStorage.getItem("token")
  const headers={Authorization:`Bearer ${token}`}

  const [sales,setSales]=useState<any[]>([])
  const [selected,setSelected]=useState<any>(null)
  const [returnQty,setReturnQty]=useState<any>({})
  const [method,setMethod]=useState("CASH")
  const [refund,setRefund]=useState<any>(null)
  const [showDeliver,setShowDeliver]=useState(false)
  const [deliverMode,setDeliverMode]=useState("CASH")

  // LOAD SALES
  useEffect(()=>{
    axios.get(`${API}/sales/`,{headers})
      .then(r=>setSales(r.data))
  },[])

  // OPEN SALE
  const openSale=async(id:number)=>{
    const res=await axios.get(`${API}/sales/${id}`,{headers})
    setSelected(res.data)
    setReturnQty({})
    setRefund(null)
  }

  // DELIVER
  const processDeliver=async()=>{
    try {
      await axios.post(
        `${API}/sales/${selected.id}/deliver`,
        { balance_payment_mode: deliverMode },
        { headers }
      )
      setShowDeliver(false)
      openSale(selected.id)
    } catch(err:any){
      alert(err.response?.data?.detail || "Delivery failed")
    }
  }

  const balanceDue = selected ? (selected.balance_amount ?? selected.balance ?? 0) : 0

  // PRINT
  const printInvoice=async(id:number)=>{
    const res=await axios.get(
      `${API}/sales/${id}/pdf`,
      {headers,responseType:"blob"}
    )
    const url=URL.createObjectURL(new Blob([res.data]))
    window.open(url)
  }

  // RETURN
  const processReturn=async()=>{

    const items=Object.keys(returnQty)
      .filter(k=>returnQty[k]>0)
      .map(k=>({
        item_id:Number(k),
        qty:returnQty[k]
      }))

    if(items.length===0){
      alert("No items selected")
      return
    }

    const res=await axios.post(
      `${API}/sales/${selected.id}/return`,
      {items,method},
      {headers}
    )

    setRefund(res.data)
  }

  return (
    <div style={{padding:30}}>

      <h1>Sales History</h1>

      {!selected && (
        <table border={1} cellPadding={6}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Total</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            {sales.map(s=>(
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.total}</td>
                <td>{s.status}</td>

                <td>
                  <button onClick={()=>openSale(s.id)}>
                    Open
                  </button>

                  <button onClick={()=>printInvoice(s.id)}>
                    Reprint
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {selected && (
        <div>

          <h2>Sale #{selected.id}</h2>

          <table border={1} cellPadding={6}>
            <thead>
              <tr>
                <th>Item</th>
                <th>Sold</th>
                <th>Return Qty</th>
              </tr>
            </thead>

            <tbody>
              {selected.items.map((i:any)=>(
                <tr key={i.item_id}>
                  <td>{i.name}</td>
                  <td>{i.qty}</td>

                  <td>
                    <input
                      type="number"
                      min={0}
                      max={i.qty}
                      value={returnQty[i.item_id] || ""}
                      onChange={e=>
                        setReturnQty({
                          ...returnQty,
                          [i.item_id]:Number(e.target.value)
                        })
                      }
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{marginTop:15}}>
            <select
              value={method}
              onChange={e=>setMethod(e.target.value)}
            >
              <option>CASH</option>
              <option>UPI</option>
              <option>CARD</option>
              <option>ADJUST</option>
            </select>
          </div>

          <button onClick={processReturn}>
            Process Return
          </button>

          {Number(balanceDue) > 0 && selected?.delivery_status !== "delivered" && (
            <button onClick={()=>setShowDeliver(true)} style={{ marginLeft: 8 }}>
              Deliver
            </button>
          )}

          <button onClick={()=>setSelected(null)} style={{ marginLeft: 8 }}>
            Back
          </button>

          {showDeliver && (
            <div style={{
              position: "fixed",
              top: 0, left: 0, right: 0, bottom: 0,
              background: "rgba(0,0,0,0.5)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 1000,
            }}>
              <div style={{
                background: "white",
                padding: 24,
                borderRadius: 8,
                minWidth: 320,
                boxShadow: "0 4px 20px rgba(0,0,0,0.2)",
              }}>
                <h3>Confirm Delivery</h3>
                <p><strong>Balance Amount: ₹ {Number(balanceDue).toFixed(2)}</strong></p>
                <div style={{ marginTop: 12 }}>
                  <label>Payment Mode</label>
                  <select
                    value={deliverMode}
                    onChange={e=>setDeliverMode(e.target.value)}
                    style={{ display: "block", marginTop: 4, padding: 8, width: "100%" }}
                  >
                    <option>CASH</option>
                    <option>UPI</option>
                    <option>CARD</option>
                    <option>BANK TRANSFER</option>
                  </select>
                </div>
                <div style={{ marginTop: 20, display: "flex", gap: 8 }}>
                  <button onClick={processDeliver}>
                    Confirm Delivery
                  </button>
                  <button onClick={()=>setShowDeliver(false)}>
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          {refund && (
            <div style={{marginTop:20}}>
              <h3>Refund ₹ {refund.refund}</h3>
              <p>Method: {refund.method}</p>
              <p>Time: {refund.time}</p>

              <button onClick={async ()=>{
                const res=await axios.get(
                  `${API}/sales/${selected.id}/return-pdf`,
                  {headers,responseType:"blob"}
                )
                const url=URL.createObjectURL(
                  new Blob([res.data])
                )
                window.open(url)
              }}>
                Print Return Receipt
              </button>
            </div>
          )}

        </div>
      )}

    </div>
  )
}
