import React, { useState  } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
 
export default function CreateSubject(){
  
    const navigate = useNavigate();
  
    const [inputs, setInputs] = useState([]);
  
    const handleChange = (event) => {
        const name = event.target.name;
        const value = event.target.value;
        setInputs(values => ({...values, [name]: value}));
    }
    const handleSubmit = (event) => {
        event.preventDefault();
  
        axios.post('http://127.0.0.1:5000/admin/subjects/create_subject', inputs).then(function(response){
            console.log(response.data);
            navigate('/subjects');
        });
          
    }
     
    return (
    <div>
        <div className="container h-100">
            <div className="row">
                <div className="col-2"></div>
                <div className="col-8">
                <h1>Create user</h1>
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                      <label>Subject_ID</label>
                      <input type="number" className="form-control" name="subject_id" onChange={handleChange} />
                    </div>
                    <div className="mb-3">
                      <label>Subject Code</label>
                      <input type="text" className="form-control" name="subject_code" onChange={handleChange} />
                    </div>
                    <div className="mb-3">
                      <label>Subject Name</label>
                      <input type="text" className="form-control" name="subject_name" onChange={handleChange} />
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