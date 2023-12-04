import React, { useEffect, useState } from 'react';
import axios from "axios"
import { Link } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';

export default function ListPrereqPage() {
    const { user } = useUser();
    const admin = user.publicMetadata.admin;

    const [prereqs, setPrereqs] = useState([]);
    useEffect(() => {
        getPrereqs();
    }, []);

    function getPrereqs() {
        axios.get(`http://127.0.0.1:5000/admin/prereqs/${admin}`).then(function (response) {
            console.log(response.data);
            setPrereqs(response.data);
        });
    }

    const deletePrereq = (id) => {
        axios.delete(`http://127.0.0.1:5000/admin/prereqs/delete/${admin}/${id}`).then(function (response) {
            console.log(response.data);
            getPrereqs();
        });
        alert("Successfully Deleted");
    }

    return (
        <div>
            <div className="container h-100">
                <div className="row h-100">
                    <div className="col-12">
                        <p><Link to="/admin-prereqs/addnewprereq" className="btn btn-success">Add New Prerequisite</Link> </p>
                        <h1>List Prerequisites</h1>
                        <table class="table table-bordered table-striped">
                            <thead>
                                <tr>
                                    <th>Prereq_ID</th>
                                    <th>Course_ID</th>
                                    <th>Prereq Courses</th>
                                    <th>Grade Required</th>
                                </tr>
                            </thead>
                            <tbody>
                                {prereqs.map((prereq, key) =>
                                    <tr key={key}>
                                        <td>{prereq.prereq_id}</td>
                                        <td>{prereq.crs_id}</td>
                                        <td>{`[${prereq.prereq_courses.join(', ')}]`}</td>
                                        <td>{prereq.grade_required}</td>                                <td>
                                            <Link to={`/admin-prereqs/prereq/${prereq.prereq_id}/edit`} className="btn btn-success" style={{ marginRight: "10px" }}>Edit</Link>
                                            <button onClick={() => deletePrereq(prereq.prereq_id)} className="btn btn-danger">Delete</button>

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