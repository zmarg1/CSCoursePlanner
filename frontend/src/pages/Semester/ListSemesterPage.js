import React, {useEffect, useState } from 'react';
import axios from "axios"
import {Link} from 'react-router-dom';

export default function ListSemesterPage(){
    const [semesters, setSemesters] = useState([]);
    useEffect(() => {
        getSemesters();
    }, []);

    function getSemesters() {
        axios.get('http://127.0.0.1:5000/admin/semesters').then(function(response) {
            console.log(response.data);
            setSemesters(response.data);
        });
    }

    const deleteSemester = (id) => {
        axios.delete(`http://127.0.0.1:5000/admin/semesters/delete/${id}`).then(function(response){
            console.log(response.data);
            getSemesters();
        });
        alert("Successfully Deleted");
    }

    return (
    <div>
        <div className="container h-100">
            <div className="row h-100">
                <div className="col-12">
                    <p><Link to ="/semesters/addnewsemester" className = "btn btn-success">Add New Semester</Link> </p>
                    <h1>List Semesters</h1>
                    <table class = "table table-bordered table-striped">
                        <thead>
                            <tr>
                                <th>Semester_ID</th>
                                <th>Term</th>
                                <th>Year</th>
                            </tr>
                        </thead>
                        <tbody>
                            {semesters.map((semester,key) =>
                                <tr key = {key}>
                                    <td>{semester.semester_id}</td>
                                    <td>{semester.term}</td>
                                    <td>{semester.year}</td>
                                <td>
                                    <Link to={`/semesters/semester/${semester.semester_id}/edit`} className="btn btn-success" style={{marginRight: "10px"}}>Edit</Link>
                                    <button onClick={() => deleteSemester(semester.semester_id)} className="btn btn-danger">Delete</button>

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