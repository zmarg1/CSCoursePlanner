import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate, useParams } from "react-router-dom";
import { useUser } from "@clerk/clerk-react";
import Config from "../../config";

export default function EditPrereq() {
  const URL = `${Config.backendURL}`
  const { user } = useUser();
  const admin = user.publicMetadata.admin;

  const navigate = useNavigate();
  const [inputs, setInputs] = useState({
    prereq_id: "",
    crs_id: "",
    prereq_courses: [],
    grade_required: "",
  });

  const { id } = useParams();

  useEffect(() => {
    getPrereq();
  }, []);

  function getPrereq() {
    axios.get(`${URL}/admin/prereqs/${admin}/${id}`).then(function (response) {
      console.log(response.data);
      setInputs(response.data);
    });
  }

  const handleChange = (event) => {
    const name = event.target.name;
    let value = event.target.value;

    console.log(value); // Debugging line

    // Convert the comma-separated string to an array of integers
    if (name === "prereq_courses") {
      value = value.split(",").map((item) => item.trim()).filter(Boolean); // Remove empty strings
    }

    setInputs((values) => ({ ...values, [name]: value }));
  };

  const handleKeyDown = (event) => {
    if (event.keyCode === 188) { // Check for the comma key
      event.preventDefault();
      setInputs((values) => ({
        ...values,
        prereq_courses: [...values.prereq_courses, ""],
      }));
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    axios
      .put(`${URL}/admin/prereqs/update_prereq/${admin}/${id}`, inputs)
      .then(function (response) {
        console.log(response.data);
        navigate('/admin-prereqs');
      });
  };

  return (
    <div>
      <div className="container h-100">
        <div className="row">
          <div className="col-2"></div>
          <div className="col-8">
            <h1>Edit Prerequisite</h1>
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label>Course_ID</label>
                <input
                  type="number"
                  value={inputs.crs_id}
                  className="form-control"
                  name="crs_id"
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="mb-3">
                <label>Prereq Courses (comma-separated)</label>
                <input
                  type="text"
                  value={inputs.prereq_courses.join(", ")}
                  className="form-control"
                  name="prereq_courses"
                  onChange={handleChange}
                  onKeyDown={handleKeyDown}
                  required
                />
              </div>
              <div className="mb-3">
                <label>Grade Required</label>
                <input
                  type="number"
                  value={inputs.grade_required}
                  className="form-control"
                  name="grade_required"
                  onChange={handleChange}
                  required
                />
              </div>
              <button type="submit" name="update" className="btn btn-primary">
                Save
              </button>
            </form>
          </div>
          <div className="col-2"></div>
        </div>
      </div>
    </div>
  );
}