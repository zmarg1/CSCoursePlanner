import React, { useState  } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
 
export default function CreatePrereq(){
  
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
  
        axios.post('http://127.0.0.1:5000/admin/prereqs/create_prereq', inputs).then(function(response){
            console.log(response.data);
            navigate('/prereqs');
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
                      <label>Prereq_ID</label>
                      <input type="number" className="form-control" name="prereq_id" onChange={handleChange} />
                    </div>
                    <div className="mb-3">
                      <label>Course_ID</label>
                      <input type="number" className="form-control" name="crs_id" onChange={handleChange} />
                    </div>
                    <div className="mb-3">
                      <label>Prereq Course (comma separated)</label>
                      <input type="text" className="form-control" name="prereq_courses" onChange={handleChange} />
                    </div>
                    <div className="mb-3">
                      <label>Grade Required</label>
                      <input type="number" className="form-control" name="grade_required" onChange={handleChange} />
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