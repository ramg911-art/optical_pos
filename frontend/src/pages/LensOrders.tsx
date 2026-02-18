import React, { useEffect, useState } from "react"
import axios from "axios"

const API = "http://192.168.10.216:9200"

const LENS_TYPES = ["Single Vision", "Bifocal", "Progressive"]
const INDEXES = ["1.49", "1.56", "1.60", "1.67", "1.74"]
const COATINGS = ["Hard Coat", "AR", "Blue Cut", "Photochromic"]
const TINTS = ["None", "Grey", "Brown", "Green"]

export default function LensOrders() {

  const token = localStorage.getItem("token")

  const headers = {
    Authorization: `Bearer ${token}`
  }

  const [orders, setOrders] = useState<any[]>([])
  const [suppliers, setSuppliers] = useState<any[]>([])

  const [form, setForm] = useState<any>({
    sale_id: "",
    lens_type: "",
    index_value: "",
    coating: "",
    tint: "",
    supplier_id: ""
  })

  const [rx, setRx] = useState<any>({
    sphere_r: "",
    cyl_r: "",
    axis_r: "",
    add_r: "",
    sphere_l: "",
    cyl_l: "",
    axis_l: "",
    add_l: "",
    pd: "",
    notes: ""
  })


  // LOAD DATA
  const load = () => {

    axios.get(`${API}/lens/`, { headers })
      .then(res => setOrders(res.data))
      .catch(err => console.error("Lens load error:", err))

    axios.get(`${API}/suppliers/`, { headers })
      .then(res => setSuppliers(res.data))
      .catch(err => console.error("Supplier load error:", err))

  }

  useEffect(() => {
    load()
  }, [])



  // LOAD RX FROM SALE
  const loadRxFromSale = async () => {

    if (!form.sale_id) {
      alert("Enter Sale ID")
      return
    }

    try {

      const res = await axios.get(
        `${API}/prescriptions/sale/${form.sale_id}`,
        { headers }
      )

      if (Object.keys(res.data).length === 0) {
        alert("No prescription found")
        return
      }

      setRx(res.data)

    }
    catch (err) {

      console.error(err)
      alert("Error loading prescription")

    }

  }



  // CREATE ORDER
  const create = async () => {

    try {

      if (!form.sale_id) {
        alert("Sale ID required")
        return
      }

      if (!form.supplier_id) {
        alert("Supplier required")
        return
      }

      const rxRes = await axios.post(
        `${API}/lens/prescription`,
        {
          sale_id: Number(form.sale_id),

          sphere_r: rx.sphere_r || null,
          cyl_r: rx.cyl_r || null,
          axis_r: rx.axis_r || null,
          add_r: rx.add_r || null,

          sphere_l: rx.sphere_l || null,
          cyl_l: rx.cyl_l || null,
          axis_l: rx.axis_l || null,
          add_l: rx.add_l || null,

          pd: rx.pd || null,
          notes: rx.notes || null
        },
        { headers }
      )

      const prescription_id = rxRes.data.id

      await axios.post(
        `${API}/lens/order`,
        {
          sale_id: Number(form.sale_id),
          prescription_id,
          supplier_id: Number(form.supplier_id),

          lens_type: form.lens_type || null,
          index_value: form.index_value || null,
          coating: form.coating || null,
          tint: form.tint || null
        },
        { headers }
      )

      alert("Lens Order Created Successfully")

      load()

    }
    catch (err: any) {

      console.error(err.response?.data)

      alert("Error creating order")

    }

  }



  // UPDATE STATUS
  const updateStatus = async (id: number, status: string) => {

    try {

      await axios.put(
        `${API}/lens/${id}/status`,
        { status },
        { headers }
      )

      load()

    }
    catch {

      alert("Status update failed")

    }

  }



  const statusColor = (status: string) => {

    if (status === "READY") return "green"
    if (status === "IN_LAB") return "orange"
    if (status === "DELIVERED") return "blue"
    return "black"

  }



  return (

    <div style={{ padding: 30 }}>

      <h1>Lens Orders</h1>

      <input
        placeholder="Sale ID"
        value={form.sale_id}
        onChange={e =>
          setForm({ ...form, sale_id: e.target.value })
        }
      />

      <button onClick={loadRxFromSale}>
        Load Rx
      </button>


      <h3>Prescription</h3>

      <table border={1} cellPadding={5}>

        <thead>
          <tr>
            <th></th>
            <th>SPH</th>
            <th>CYL</th>
            <th>AXIS</th>
            <th>ADD</th>
          </tr>
        </thead>

        <tbody>

          <tr>
            <td>OD</td>
            <td><input value={rx.sphere_r || ""} onChange={e => setRx({ ...rx, sphere_r: e.target.value })}/></td>
            <td><input value={rx.cyl_r || ""} onChange={e => setRx({ ...rx, cyl_r: e.target.value })}/></td>
            <td><input value={rx.axis_r || ""} onChange={e => setRx({ ...rx, axis_r: e.target.value })}/></td>
            <td><input value={rx.add_r || ""} onChange={e => setRx({ ...rx, add_r: e.target.value })}/></td>
          </tr>

          <tr>
            <td>OS</td>
            <td><input value={rx.sphere_l || ""} onChange={e => setRx({ ...rx, sphere_l: e.target.value })}/></td>
            <td><input value={rx.cyl_l || ""} onChange={e => setRx({ ...rx, cyl_l: e.target.value })}/></td>
            <td><input value={rx.axis_l || ""} onChange={e => setRx({ ...rx, axis_l: e.target.value })}/></td>
            <td><input value={rx.add_l || ""} onChange={e => setRx({ ...rx, add_l: e.target.value })}/></td>
          </tr>

        </tbody>

      </table>


      <h3>Lens Configuration</h3>

      <select onChange={e => setForm({ ...form, lens_type: e.target.value })}>
        <option value="">Lens Type</option>
        {LENS_TYPES.map(t => <option key={t}>{t}</option>)}
      </select>

      <select onChange={e => setForm({ ...form, index_value: e.target.value })}>
        <option value="">Index</option>
        {INDEXES.map(i => <option key={i}>{i}</option>)}
      </select>

      <select onChange={e => setForm({ ...form, coating: e.target.value })}>
        <option value="">Coating</option>
        {COATINGS.map(c => <option key={c}>{c}</option>)}
      </select>

      <select onChange={e => setForm({ ...form, tint: e.target.value })}>
        <option value="">Tint</option>
        {TINTS.map(t => <option key={t}>{t}</option>)}
      </select>

      <select onChange={e => setForm({ ...form, supplier_id: e.target.value })}>
        <option value="">Supplier</option>
        {suppliers.map(s =>
          <option key={s.id} value={s.id}>{s.name}</option>
        )}
      </select>


      <br /><br />

      <button onClick={create}>
        Create Lens Order
      </button>


      <h3>Orders</h3>

      <table border={1} cellPadding={6}>

        <thead>
          <tr>
            <th>ID</th>
            <th>Patient</th>
            <th>Phone</th>
            <th>Supplier</th>
            <th>Lens</th>
            <th>Index</th>
            <th>Status</th>
            <th>Order Date</th>
            <th>Expected</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>

          {orders.map(o => (

            <tr key={o.id}
              style={{
                backgroundColor:
                  o.status === "READY" ? "#d4edda" : ""
              }}
            >

              <td>{o.id}</td>
              <td>{o.patient_name}</td>
              <td>{o.patient_phone}</td>
              <td>{o.supplier}</td>
              <td>{o.lens_type}</td>
              <td>{o.index_value}</td>

              <td style={{ color: statusColor(o.status), fontWeight: "bold" }}>
                {o.status}
              </td>

              <td>{o.order_date}</td>
              <td>{o.expected_date}</td>

              <td>

                <button onClick={() => updateStatus(o.id, "ORDERED")}>Ordered</button>
                <button onClick={() => updateStatus(o.id, "IN_LAB")}>Lab</button>
                <button onClick={() => updateStatus(o.id, "READY")}>Ready</button>
                <button onClick={() => updateStatus(o.id, "DELIVERED")}>Delivered</button>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>

  )

}
