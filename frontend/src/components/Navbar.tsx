import { useNavigate } from "react-router-dom"

export default function Navbar() {

  const nav = useNavigate()

  return (
    <div className="bg-indigo-600 text-white px-6 py-3 shadow-md flex justify-between items-center">

      {/* LEFT */}
      <div className="font-bold text-xl cursor-pointer"
           onClick={()=>nav("/dashboard")}>
        Optical POS
      </div>

      {/* RIGHT */}
      <div className="flex gap-3">

        <button onClick={()=>nav("/sales")} className="navbtn">
          Billing
        </button>

        <button onClick={()=>nav("/items")} className="navbtn">
          Items
        </button>

        <button onClick={()=>nav("/suppliers")} className="navbtn">
          Suppliers
        </button>

        <button onClick={()=>nav("/lens")} className="navbtn">
          Lens
        </button>

        <button onClick={()=>nav("/history")} className="navbtn">
          Sales
        </button>

        <button
          onClick={()=>{
            localStorage.removeItem("token")
            nav("/")
          }}
          className="bg-red-500 hover:bg-red-600 px-3 py-1 rounded"
        >
          Logout
        </button>

      </div>
    </div>
  )
}
