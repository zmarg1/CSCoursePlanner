import React, { useState, useEffect  } from "react";
import axios from "axios";
import { useNavigate, useParams } from "react-router-dom";
 
export default function EditCourse(){
  
    const navigate = useNavigate();
  
    const [inputs, setInputs] = useState([]);
  
    const {id} = useParams();
  
    useEffect(() => {
        getCourse();
    }, []);
  
    function getCourse() {
        axios.get(`http://127.0.0.1:5000/admin/courses/${id}`).then(function(response) {
            console.log(response.data);
            setInputs(response.data);
        });
    }
  
    const handleChange = (event) => {
        const name = event.target.name;
        const value = event.target.value;
        setInputs(values => ({...values, [name]: value}));
    }
    const handleSubmit = (event) => {
        event.preventDefault();
  
        axios.put(`http://127.0.0.1:5000/admin/courses/update_course/${id}`, inputs).then(function(response){
            console.log(response.data);
            navigate('/');
        });
          
    }
     
    return (
    <div>
        <div className="container h-100">
        <div className="row">
            <div className="col-2"></div>
            <div className="col-8">
            <h1>Edit Course</h1>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label>Subject_ID</label>
                  <input type="number" value={inputs.subject_id} className="form-control" name="subject_id" onChange={handleChange} />
                </div>
                <div className="mb-3">
                  <label>Course Title</label>
                  <input type="text" value={inputs.crs_title} className="form-control" name="crs_title" onChange={handleChange} />
                </div>
                <div className="mb-3">
                  <label>Course Number</label>
                  <input type="text" value={inputs.crs_num} className="form-control" name="crs_num" onChange={handleChange} />
                </div>
                <div className="mb-3">
                  <label>Credits</label>
                  <input type="number" value={inputs.credits} className="form-control" name="credits" onChange={handleChange} />
                </div>   
                <button type="submit" name="update" className="btn btn-primary">Save</button>
            </form>
            </div>
            <div className="col-2"></div>
        </div>
        </div>
    </div>
  );
}