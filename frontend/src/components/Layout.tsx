import Navbar from "./Navbar"

export default function Layout({children}:any){
  return (
    <div>

      <Navbar/>

      <div className="p-6">
        {children}
      </div>

    </div>
  )
}
