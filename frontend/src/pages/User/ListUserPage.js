import React, { useEffect, useState } from 'react';
import axios from "axios"
import { Link } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';

export default function ListUserPage() {
    const { user } = useUser();
    const admin = user.publicMetadata.admin;

    const [users, setUsers] = useState([]);
    useEffect(() => {
        getUsers();
    }, []);

    function getUsers() {
        axios.get(`http://127.0.0.1:5000/admin/users/${admin}`).then(function (response) {
            console.log(response.data);
            setUsers(response.data);
        });
    }

    const deleteUser = (id) => {
        axios.delete(`http://127.0.0.1:5000/admin/users/delete/${admin}/${id}`).then(function (response) {
            console.log(response.data);
            getUsers();
        });
        alert("Successfully Deleted");
    }

    return (
        <div>
            <div className="container h-100">
                <div className="row h-100">
                    <div className="col-12">
                        <p><Link to="/admin-users/addnewuser" className="btn btn-success">Add New User</Link> </p>
                        <h1>List Users</h1>
                        <table class="table table-bordered table-striped">
                            <thead>
                                <tr>
                                    <th>User_ID</th>
                                    <th>Email</th>
                                    <th>Campus_ID</th>
                                    <th>First Name</th>
                                    <th>Last Name</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map((user, key) =>
                                    <tr key={key}>
                                        <td>{user.user_id}</td>
                                        <td>{user.email}</td>
                                        <td>{user.campus_id}</td>
                                        <td>{user.first_name}</td>
                                        <td>{user.last_name}</td>
                                        <td>
                                            <Link to={`/admin-users/user/${user.user_id}/edit`} className="btn btn-success" style={{ marginRight: "10px" }}>Edit</Link>
                                            <button onClick={() => deleteUser(user.user_id)} className="btn btn-danger">Delete</button>

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