import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate, useParams } from "react-router-dom";
import { useUser } from "@clerk/clerk-react";
import Config from "../../../config";

export default function EditDegree() {
    const URL = `${Config.backendURL}`
    const { user } = useUser();
    const admin = user.publicMetadata.admin;

    const navigate = useNavigate();

    const [inputs, setInputs] = useState([]);

    const { id } = useParams();

    useEffect(() => {
        getDegree();
    }, []);

    function getDegree() {
        axios.get(`${URL}/admin/degrees/${admin}/${id}`).then(function (response) {
            console.log(response.data);
            setInputs(response.data);
        });
    }

    const handleChange = (event) => {
        const name = event.target.name;
        const value = event.target.value;
        setInputs(values => ({ ...values, [name]: value }));
    }
    const handleSubmit = (event) => {
        event.preventDefault();

        axios.put(`${URL}/admin/degrees/update_degree/${admin}/${id}`, inputs).then(function (response) {
            console.log(response.data);
            navigate('/admin-degrees');
        });

    }

    return (
        <div>
            <div className="container h-100">
                <div className="row">
                    <div className="col-2"></div>
                    <div className="col-8">
                        <h1>Edit Degree</h1>
                        <form onSubmit={handleSubmit}>
                            <div className="mb-3">
                                <label>Degree Name</label>
                                <input type="text" value={inputs.term} className="form-control" name="deg_name" onChange={handleChange} required/>
                            </div>
                            <div className="mb-3">
                                <label>Degree Type</label>
                                <input type="text" value={inputs.year} className="form-control" name="deg_type" onChange={handleChange} required/>
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