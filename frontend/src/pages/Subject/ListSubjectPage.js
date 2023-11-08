import React, {useEffect, useState } from 'react';
import axios from "axios"
import {Link} from 'react-router-dom';

export default function ListSubjectPage(){
    const [subjects, setSubjects] = useState([]);
    useEffect(() => {
        getSubjects();
    }, []);

    function getSubjects() {
        axios.get('http://127.0.0.1:5000/admin/subjects').then(function(response) {
            console.log(response.data);
            setSubjects(response.data);
        });
    }

    const deleteSubject = (id) => {
        axios.delete(`http://127.0.0.1:5000/admin/subjects/delete/${id}`).then(function(response){
            console.log(response.data);
            getSubjects();
        });
        alert("Successfully Deleted");
    }

    return (
    <div>
        <div className="container h-100">
            <div className="row h-100">
                <div className="col-12">
                    <p><Link to ="/subjects/addnewsubject" className = "btn btn-success">Add New Subject</Link> </p>
                    <h1>List Subjects</h1>
                    <table class = "table table-bordered table-striped">
                        <thead>
                            <tr>
                                <th>Subject_ID</th>
                                <th>Subject Code</th>
                                <th>Subject Name</th>
                            </tr>
                        </thead>
                        <tbody>
                            {subjects.map((subject,key) =>
                                <tr key = {key}>
                                    <td>{subject.subject_id}</td>
                                    <td>{subject.subject_code}</td>
                                    <td>{subject.subject_name}</td>
                                <td>
                                    <Link to={`/subjects/subject/${subject.subject_id}/edit`} className="btn btn-success" style={{marginRight: "10px"}}>Edit</Link>
                                    <button onClick={() => deleteSubject(subject.subject_id)} className="btn btn-danger">Delete</button>

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