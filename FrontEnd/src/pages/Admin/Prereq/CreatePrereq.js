import React, { useState  } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useUser } from "@clerk/clerk-react";
import Config from "../../../config";
 
export default function CreatePrereq(){
  const URL = `${Config.backendURL}`
  const {user} = useUser();
    const admin = user.publicMetadata.admin;
  
    const navigate = useNavigate();
  
    const [inputs, setInputs] = useState({
      prereq_id: "",
      crs_id: "",
      prereq_courses: [],
      grade_required: "",
    });

    const handleChange = (event) => {
      const name = event.target.name;
      let value = event.target.value;
  
      // Convert the comma-separated string to an array of integers
      if (name === "prereq_courses") {
        value = value.split(",").map(Number);
      }
  
      setInputs((values) => ({ ...values, [name]: value }));
    };

    const handleSubmit = (event) => {
        event.preventDefault();
  
        axios.post(`${URL}/admin/prereqs/create_prereq/${admin}`, inputs).then(function(response){
            console.log(response.data);
            navigate('/admin-prereqs');
        });
          
    }
     
    return (
    <div>
        <div className="container h-100">
            <div className="row">
                <div className="col-2"></div>
                <div className="col-8">
                <h1>Create Prerequisite</h1>
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                      <label>Course_ID</label>
                      <input type="number" className="form-control" name="crs_id" onChange={handleChange} required/>
                    </div>
                    <div className="mb-3">
                      <label>Prereq Courses (comma separated)</label>
                      <input type="text" className="form-control" name="prereq_courses" onChange={handleChange} required/>
                    </div>
                    <div className="mb-3">
                      <label>Grade Required</label>
                      <input type="number" className="form-control" name="grade_required" onChange={handleChange} required/>
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