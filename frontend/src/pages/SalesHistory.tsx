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

          <button onClick={()=>setSelected(null)}>
            Back
          </button>

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
