import React, { useState, useEffect } from "react";
import api from './interceptor/api';

import "./FileVersions.css";

function FileVersionsList(props) {
  const file_versions = props.file_versions;
  return file_versions.map((file_version) => (
    <div className="file-version" key={file_version.id}>
      <h2>File Name: {file_version.file_name}</h2>
      <p>
        ID: {file_version.id} Version: {file_version.version_number}
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
      api.post('/file_versions/', formData, axiosConfig).then(
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
      const response = await api.get('/file_versions/');
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

  );
}

export default FileVersions;
