import React, { useState  } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
 
export default function CreateCourse(){
  
    const navigate = useNavigate();
  
    const [inputs, setInputs] = useState([]);
  
    const handleChange = (event) => {
        const name = event.target.name;
        const value = event.target.value;
        setInputs(values => ({...values, [name]: value}));
    }
    const handleSubmit = (event) => {
        event.preventDefault();
  
        axios.post('http://127.0.0.1:5000/admin/courses/create_course', inputs).then(function(response){
            console.log(response.data);
            navigate('/courses/');
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
                      <label>Course_ID</label>
                      <input type="number" className="form-control" name="course_id" onChange={handleChange} />
                    </div>
                    <div className="mb-3">
                      <label>Subject_ID</label>
                      <input type="number" className="form-control" name="subject_id" onChange={handleChange} />
                    </div>
                    <div className="mb-3">
                      <label>Course Title</label>
                      <input type="text" className="form-control" name="crs_title" onChange={handleChange} />
                    </div>
                    <div className="mb-3">
                      <label>Course Number</label>
                      <input type="text" className="form-control" name="crs_num" onChange={handleChange} />
                    </div>
                    <div className="mb-3">
                      <label>Credits</label>
                      <input type="num" className="form-control" name="credits" onChange={handleChange} />
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