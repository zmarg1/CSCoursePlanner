import React, { useEffect, useState } from 'react';
import axios from "axios"
import { Link } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';

export default function ListDegreePage() {
    const { user } = useUser();
    const admin = user.publicMetadata.admin;

    const [degrees, setDegrees] = useState([]);

    useEffect(() => {
        getDegrees();
    }, []);

    function getDegrees() {
        axios.get(`http://127.0.0.1:5000/admin/degrees/${admin}`).then(function (response) {
            console.log(response.data);
            setDegrees(response.data);
        });
    }

    const deleteDegree = (id) => {
        axios.delete(`http://127.0.0.1:5000/admin/degrees/delete/${admin}/${id}`).then(function (response) {
            console.log(response.data);
            getDegrees();
        });
        alert("Successfully Deleted");
    }

    return (
        <div>
            <div className="container h-100">
                <div className="row h-100">
                    <div className="col-12">
                        <p><Link to="/degrees/addnewdegree" className="btn btn-success">Add New Degree</Link> </p>
                        <h1>List Degrees</h1>
                        <table class="table table-bordered table-striped">
                            <thead>
                                <tr>
                                    <th>Degree_ID</th>
                                    <th>Degree Name</th>
                                    <th>Degree Type</th>
                                </tr>
                            </thead>
                            <tbody>
                                {degrees.map((degree, key) =>
                                    <tr key={key}>
                                        <td>{degree.degree_id}</td>
                                        <td>{degree.deg_name}</td>
                                        <td>{degree.deg_type}</td>
                                        <td>
                                            <Link to={`/admin-degrees/degree/${degree.degree_id}/edit`} className="btn btn-success" style={{ marginRight: "10px" }}>Edit</Link>
                                            <button onClick={() => deleteDegree(degree.degree_id)} className="btn btn-danger">Delete</button>

                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}