import React, { useState  } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useUser } from "@clerk/clerk-react";
import Config from "../../config";
 
export default function CreateSubject(){
  const URL = `${Config.backendURL}`
  const {user} = useUser();
    const admin = user.publicMetadata.admin;
  
    const navigate = useNavigate();
  
    const [inputs, setInputs] = useState([]);
  
    const handleChange = (event) => {
        const name = event.target.name;
        const value = event.target.value;
        setInputs(values => ({...values, [name]: value}));
    }
    const handleSubmit = (event) => {
        event.preventDefault();
  
        axios.post(`${URL}/admin/subjects/create_subject/${admin}`, inputs).then(function(response){
            console.log(response.data);
            navigate('/admin-subjects');
        });
          
    }
     
    return (
    <div>
        <div className="container h-100">
            <div className="row">
                <div className="col-2"></div>
                <div className="col-8">
                <h1>Create Subject</h1>
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                      <label>Subject Code</label>
                      <input type="text" className="form-control" name="subject_code" onChange={handleChange} required/>
                    </div>
                    <div className="mb-3">
                      <label>Subject Name</label>
                      <input type="text" className="form-control" name="subject_name" onChange={handleChange} required/>
                    </div>
                    <button type="submit" name="add" className="btn btn-primary">Save</button>
                </form>
                </div>
                <div className="col-2"></div>
            </div>
        </div>
    </div>
  );
}