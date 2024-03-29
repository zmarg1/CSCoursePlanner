import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useUser } from "@clerk/clerk-react";
import Config from "../../../config";

export default function CreateSemester() {
  const URL = `${Config.backendURL}`
  const { user } = useUser();
  const admin = user.publicMetadata.admin;

  const navigate = useNavigate();

  const [inputs, setInputs] = useState([]);

  const handleChange = (event) => {
    const name = event.target.name;
    const value = event.target.value;
    setInputs(values => ({ ...values, [name]: value }));
  }
  const handleSubmit = (event) => {
    event.preventDefault();

    axios.post(`${URL}/admin/semesters/create_semester/${admin}`, inputs).then(function (response) {
      console.log(response.data);
      navigate('/admin-semesters');
    });

  }

  return (
    <div>
      <div className="container h-100">
        <div className="row">
          <div className="col-2"></div>
          <div className="col-8">
            <h1>Create Semester</h1>
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label>Term</label>
                <input type="text" className="form-control" name="term" onChange={handleChange} required/>
              </div>
              <div className="mb-3">
                <label>Year</label>
                <input type="number" className="form-control" name="year" onChange={handleChange} required/>
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