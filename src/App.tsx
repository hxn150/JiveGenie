import { Route, Routes } from "react-router-dom";
import JiveGenie from "@/pages/index";

function App() {

  return (
    <Routes>
      <Route element={<JiveGenie />} path="/" />
    </Routes>
  );
}

export default App;
 