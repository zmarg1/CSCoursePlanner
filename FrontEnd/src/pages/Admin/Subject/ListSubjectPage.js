import React, {useEffect, useState } from 'react';
import axios from "axios"
import {Link} from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import Config from '../../../config';

export default function ListSubjectPage(){
    const URL = `${Config.backendURL}`
    const {user} = useUser();
    const admin = user.publicMetadata.admin;

    const [subjects, setSubjects] = useState([]);
    useEffect(() => {
        getSubjects();
    }, []);

    function getSubjects() {
        axios.get(`${URL}/admin/subjects/${admin}`).then(function(response) {
            console.log("Subjects Response",response.data);
            setSubjects(response.data);
        });
    }

    const deleteSubject = (id) => {
        axios.delete(`${URL}/admin/subjects/delete/${admin}/${id}`).then(function(response){
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
                    <p><Link to ="/admin-subjects/addnewsubject" className = "btn btn-success">Add New Subject</Link> </p>
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
                                    <td>{subject.sub_code}</td>
                                    <td>{subject.sub_name}</td>
                                <td>
                                    <Link to={`/admin-subjects/subject/${subject.subject_id}/edit`} className="btn btn-success" style={{marginRight: "10px"}}>Edit</Link>
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