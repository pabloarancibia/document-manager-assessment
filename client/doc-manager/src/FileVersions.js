import React, { useState, useEffect } from "react";
import api from './interceptor/api';
import { useNavigate } from 'react-router-dom';

import "./FileVersions.css";

function FileVersionsList(props) {
  const file_versions = props.file_versions;
  const [hoveredFile, setHoveredFile] = useState(null);

  // Download file
  const downloadFile = (urlSetted, fileName, version) => {
    const downloadUrl = `/api/${urlSetted}/${fileName}${version ? `?revision=${version}` : ''}`;
    api.get(downloadUrl, { responseType: 'blob' })
      .then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', fileName);
        document.body.appendChild(link);
        link.click();
      })
      .catch(error => {
        console.log(error);
      });
  };

  const handleMouseEnter = (file_version) => {
    setHoveredFile(file_version);
  };

  const handleMouseLeave = () => {
    setHoveredFile(null);
  };


  return file_versions.map((file_version) => (
    <div className="file-version" key={file_version.id} 
    onClick={() => downloadFile(file_version.url_setted,file_version.file_name, file_version.version_number)}
    onMouseEnter={() => handleMouseEnter(file_version)}
    onMouseLeave={handleMouseLeave}
    style={{
        backgroundColor: hoveredFile === file_version ? 'lightblue' : 'transparent',
        cursor: hoveredFile === file_version ? 'pointer' : 'default'
      }}
    >
      <h2>File Name: {file_version.file_name}</h2>
      <p>
        ID: {file_version.id} Version: {file_version.version_number}
      </p>
      <p>
        Url: {file_version.url_setted}
      </p>
    </div>
  ));
}
function FileVersions() {
  const [data, setData] = useState([]);
  console.log(data);

  const [filename, setFilename] = useState('')
  const [files, setFiles] = useState([{}])
  const [status, setstatus] = useState('')
  const [url_setted, setUrlsetted] = useState('')

  const navigate = useNavigate();

  // Logout
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  }

  // upload file
  const saveFile = () =>{
      console.log('Button clicked')

      let formData = new FormData();
      formData.append("url_file", filename);
      formData.append("url_setted", url_setted);


      let axiosConfig = {
          headers: {
              'Content-Type': 'multipart/form-data'
          }
      }

      console.log(formData)
      console.log('FormData values:');
      formData.forEach((value, key) => {
        console.log(`${key}: ${value}`);
      });
      api.post('/api/file_versions/', formData, axiosConfig).then(
          response =>{
              console.log(response)
              setstatus('File Uploaded Successfully')
          }
      ).catch(error =>{
          console.log(error)
      })
    }


  // fetch data
  const dataFetch = async () => {
    try {
      const response = await api.get('/api/file_versions/');
      // set state when the data received
      setData(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    dataFetch();
  }, []);
  return (
    <div>
      <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <div className="container-fluid">
          <span className="navbar-brand mb-0 h1">FileVersions</span>
          <div className="navbar-nav ml-auto">
            <button className="btn btn-outline-primary" onClick={handleLogout}>Logout</button>
          </div>
        </div>
      </nav>
    <div className="container mt-5">
      <h1>Upload Files</h1>
      <div className="row">
      <div className="col-md-4">
        <form>
          <div className="form-group">
          <label htmlFor="" className="float-left">
              URL (example: docs/pdf): 
            </label>
            <input
              type="text"
              value={url_setted}
              onChange={(e) => setUrlsetted(e.target.value)}
              className="form-control"
            />
            <br/>
            <label htmlFor="" className="float-left">
              Browse A File To Upload
            </label>
            
            <input
              type="file"
              onChange={e => setFilename(e.target.files[0])}
              className="form-control"
            />
          </div>
          <button type="button" onClick={saveFile} className="btn btn-primary float-left mt-2">Submit</button>
            <br/>
            <br/>
            <br/>

            {status ? <h2>{status}</h2>:null}

        </form>
      </div>
      </div>

      <h1>Found {data.length} File Versions</h1>
      <div>
        <FileVersionsList file_versions={data} />
        </div>
    </div>
    </div>

  );
}

export default FileVersions;
