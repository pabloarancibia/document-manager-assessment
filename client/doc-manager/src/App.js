import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import FileVersions from './FileVersions'
import Login from './components/Login';


// function App() {
const App = () => {
  return (
    // <div className="App">
    //   <header className="App-header">
    //     <FileVersions />
    //   </header>
    // </div>
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/home" element={<FileVersions/>} />
      </Routes>
    </Router>
  );
}

export default App;
