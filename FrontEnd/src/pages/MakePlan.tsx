import React, { useState, useEffect } from 'react';
import { StyledSelect } from '../common/select/styles';
import { StyledButton } from '../common/Button/styles';
import { StyledLabel } from '../common/Label';
import { supabase } from '../utils/supabaseClient';
import { useUser } from '@clerk/clerk-react';
import '../common/PlanStyling/Plan.css';
import { useNavigate } from 'react-router-dom';
import { notification } from "antd";
import { StyledContainer } from '../common/Container/styles';
import Config from '../config'; // Import your configuration file  

const URL = `${Config.backendURL}`

interface Course {
  course_id: number;
  course_num: string;
  course_title: string;
  credits: number;
  subject_code: string;
}

interface SemesterFromServer {
  semester_id: number;
  term: string;
  year: number;
}

interface Semester {
  id: number;
  name: string;
}

interface PlanFromServer {
  plan_id: number;
  user_id: string;
  plan_num: number;
  plan_name: string
}

interface Plan {
  id: number;
  name: string;
}

interface CourseData {
  [year: string]: { [term: string]: Course[]; };
}

const MakePlan: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useUser();
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState('');
  const [selectedCourseTitle, setSelectedCourseTitle] = useState('');
  const [semesters, setSemesters] = useState<Semester[]>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [selectedSemesterId, setSelectedSemesterId] = useState('');
  const [selectedPlanId, setSelectedPlanId] = useState('');
  const [studentStatus, setStudentStatus] = useState('');
  const [semesterCourses, setSemesterCourses] = useState<CourseData>({});
  const [isCreatePlanModalVisible, setIsCreatePlanModalVisible] = useState(false);
  const [customPlanName, setCustomPlanName] = useState('');
  const [showPreview, setShowPreview] = useState(false);


  const handleConfirmCreatePlan = async () => {
    setIsCreatePlanModalVisible(false);

    const planName = customPlanName.trim() !== '' ? customPlanName : 'Default Plan Name';
    setCustomPlanName('');

    const userEmail = user?.emailAddresses[0]?.emailAddress;
    if (!userEmail) {
      console.error('User email is not available');
      return;
    }

    try {
      const response = await fetch(`${URL}/user/plan/make-plan/${userEmail}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ plan_name: planName })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Plan creation result:', result);

      if (result.Success) {
        // Assuming the result contains the ID of the newly created plan
        const newPlanId = result.plan_id;
        await renamePlan(userEmail, newPlanId, "New Custom Name");
      } else {
        openPlanNotificationFailed(result.Failed);
      }
      await fetchPlans();

    } catch (error) {
      console.error('There was an error creating the plan:', error);
    }
  };

  const renamePlan = async (userEmail: string, planId: number, newName: string) => {
    try {
      const renameResponse = await fetch(`${URL}/user/plan/rename-plan/${userEmail}/${planId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ new_name: newName })
      });

      if (!renameResponse.ok) {
        throw new Error(`HTTP error! status: ${renameResponse.status}`);
      }

      const renameResult = await renameResponse.json();
      if (renameResult.Success) {
        openPlanNotificationSuccess(`Plan renamed to "${newName}" successfully.`);
      } else {
        openPlanNotificationFailed(renameResult.Failed);
      }

    } catch (error) {
      console.error('Error renaming plan:', error);
    }
  };



  // const determineStudentStatus = (semesterCount: number) => {
  //   if (semesterCount < 2) return 'Freshman';
  //   if (semesterCount < 4) return 'Sophomore';
  //   if (semesterCount < 6) return 'Junior';
  //   return 'Senior';
  // };

  const openPlanNotificationSuccess = (title: string) => {
    notification["success"]({
      message: "Plan Created Successfully",
      description: `Your plan "${title}" has been created!`,
      duration: 10,
    });
  };

  const openPlanNotificationFailed = (response: string) => {
    notification["error"]({
      message: "Plan Failed To Be Created",
      description: `${response}`,
      duration: 10,
    });
  };

  const openAddClassNotificationSuccess = (courseTitle: string) => {
    notification["success"]({
      message: "Class Added Successfully",
      description: `The class "${courseTitle}" has been added to your plan.`,
      duration: 10,
    });
  };

  const openAddClassNotificationFailed = (response: string) => {
    notification["error"]({
      message: "Failed To Add Course",
      description: `${response}`,
      duration: 10,
    });
  };


  const handleViewPlanClick = () => {
    const userEmail = user?.emailAddresses[0]?.emailAddress;
    navigate(`/user/plan/view-plan/${userEmail}`);
  };

  const fetchPlans = async () => {
    try {
      const email = user?.emailAddresses
      const response = await fetch(`${URL}/user/plan/view-all-plans/${email}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const plansData: PlanFromServer[] = await response.json();
      const sortedPlans = plansData.sort((a, b) => a.plan_name.localeCompare(b.plan_name));

      // Assuming you want to set the plan IDs in a state
      setPlans(sortedPlans.map(plan => ({
        id: plan.plan_id,
        name: `${plan.plan_name}`
        // You can add more fields if you have additional data for each plan
      })));
    } catch (error) {
      console.error('Error fetching plans:', error);
    }
  };

  const handleCreatePlan = () => {
    setIsCreatePlanModalVisible(true);
  };



  const fetchCourses = async (plan_id: string, sem_id: string) => {
    try {
      const email = user?.emailAddresses
      const response = await fetch(`${URL}/user/view-all-courses/${email}/${plan_id}/${sem_id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      let coursesData;
      try {
        coursesData = await response.json();
      } catch (jsonParseError) {
        console.error('Error parsing JSON:', jsonParseError);
        const rawResponse = await response.text();
        console.log('Raw response:', rawResponse);
        return;
      }

      // Sort by Course Num
      const sortedCoursesData = coursesData.sort((a: Course, b: Course) => {
        const courseNumA = parseInt(a.course_num, 10);
        const courseNumB = parseInt(b.course_num, 10);
        return courseNumA - courseNumB;
      });

      setCourses(sortedCoursesData.map((course: Course) => ({
        course_id: course.course_id,
        course_num: course.course_num,
        course_title: course.course_title,
        credits: course.credits,
        subject_code: course.subject_code,
      })));

      if (coursesData && coursesData.length > 0) {
        setShowPreview(true);
        // existing logic to set courses...
      } else {
        setShowPreview(false);
      }
    } catch (error) {
      console.error('There has been a problem with your fetch operation:', error);
      setShowPreview(false);
    }
  };

  const fetchSemesters = async () => {
    try {
      const response = await fetch(`${URL}/user/view-all-semesters`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const semestersData: SemesterFromServer[] = await response.json();

      setSemesters(semestersData.map(semester => ({
        id: semester.semester_id,
        name: `${semester.term} ${semester.year}`
      })));
    } catch (error) {
      console.error('Error fetching semesters:', error);
    }
  };

  const viewSemesterCourses = async (plan_id: string, sem_id: string) => {
    try {
      const email = user?.emailAddresses
      const response = await fetch(`${URL}//user/plan/view-semester-courses/${email}/${plan_id}/${sem_id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();

      if (!data.Failed) {
        console.log("Semester Courses Data:", data);
        setSemesterCourses(data);
      }

    }
    catch (error) {
      console.error('Error viewing semester:', error);
    }
  };

  const fetchUserDataFromSupabase = async () => {
    if (user) {
      try {
        const { data, error } = await supabase
          .from('public_user_info') // Replace with your table name
          .select('*')
          .eq('user_id', user.id); // Adjust as per your Supabase table's user ID column

        if (error) throw error;

        console.log('Fetched user-specific data:', data);
        // Handle the fetched data (e.g., set it to a state)
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    }
  };

  useEffect(() => {
    fetchPlans();
    fetchSemesters();
    fetchUserDataFromSupabase();
  }, [user]);

  const handleAddClass = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();  // Prevent the form from causing a page reload
    try {
      const email = user?.emailAddresses
      const response = await fetch(`http://127.0.0.1:5000/user/plan/add-course-to-plan/${email}/${selectedPlanId}/${selectedCourseId}/${selectedSemesterId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const result = await response.json()

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (result.Success) {
        openAddClassNotificationSuccess(result.Success)
        viewSemesterCourses(selectedPlanId, selectedSemesterId);
        fetchCourses(selectedPlanId, selectedSemesterId)
      }
      else {
        openAddClassNotificationFailed(result.Failed)
      }

    } catch (error) {
      console.error('Error adding class to plan:', error);
    }
  };

  const handleCourseSelection = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedTitle = event.target.options[event.target.selectedIndex].text;
    setSelectedCourseTitle(selectedTitle);
    setSelectedCourseId(event.target.value);
  };

  const handleSemesterSelection = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedSemesterId(event.target.value);
    if (selectedPlanId) {
      viewSemesterCourses(selectedPlanId, event.target.value);
      fetchCourses(selectedPlanId, event.target.value);
    }
  };

  const handlePlanSelection = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedPlanId(event.target.value);
    if (selectedSemesterId) {
      viewSemesterCourses(event.target.value, selectedSemesterId);
      fetchCourses(event.target.value, selectedSemesterId);
    }
  };

  return (
    <StyledContainer className="make-plan">
      <div className="grid-container">
        <div className="form-section">
          <h2>Make Your Plan</h2>
          <StyledButton color="#fdb515" onClick={handleCreatePlan} style={{ marginBottom: '30px' }}>Create Plan</StyledButton>

          <form onSubmit={handleAddClass}>

            <StyledLabel htmlFor="plan-dropdown">Select a plan:</StyledLabel>
            <StyledSelect
              value={selectedPlanId}
              onChange={handlePlanSelection}
              required
              color="#fdb515">
              <option value="">Select a Plan</option>
              {plans.map(plan => (
                <option key={plan.id} value={plan.id}>{plan.name}</option>
              ))}
            </StyledSelect>

            <StyledLabel htmlFor="semester-dropdown">Select a term:</StyledLabel>
            <StyledSelect
              id="semester-dropdown"
              value={selectedSemesterId}
              onChange={handleSemesterSelection}
              required
              color="#fdb515">
              <option key="" value="">Select a term</option>
              {semesters.map((semester, index) => (
                <option key={semester.id || index} value={semester.id}>
                  {semester.name}
                </option>
              ))}
            </StyledSelect>

            <StyledLabel htmlFor="course-dropdown">Select a class:</StyledLabel>
            <StyledSelect
              id="course-dropdown"
              value={selectedCourseId}
              onChange={handleCourseSelection}
              required
              color="#fdb515">
              <option key="" value="" title="">Select a class</option>
              {courses.map((course) => (
                <option key={course.course_id} value={course.course_id} title={course.course_title}>
                  {course.subject_code} {course.course_num}: {course.course_title} {course.credits}cr
                </option>
              ))}
            </StyledSelect>
            <StyledContainer className='button-container-makePlan' style={{ marginTop: '10%', marginLeft: '-9%' }}>
              <StyledButton color="#fdb515" onclick={handleAddClass} type="submit">Add Course</StyledButton>
              <StyledButton color="#fdb515" onClick={handleViewPlanClick}>View Plans</StyledButton>
            </StyledContainer>
          </form>
        </div>

        {showPreview && (
        <div className="terms-section">
          {Object.entries(semesterCourses).map(([year, terms]) => (
            Object.entries(terms).filter(([_, coursesList]) => coursesList.length > 0)
              .map(([term, coursesList]) => (
                <div key={term} className="term">
                  <h6 style={{ color: '#333' }}>{term} {year}</h6>
                  <ul style={{ listStyleType: 'none', paddingLeft: '5px' }}>
                    {coursesList.map((course, index) => (
                      <li key={index} style={{ display: 'flex', alignItems: 'left', marginBottom: '10px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'left' }}>
                          <strong>{course.course_title} - {course.subject_code} {course.course_num}, {course.credits} credits</strong>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              ))
          ))}
        </div> )}

        {isCreatePlanModalVisible && (
          <div className="modal-overlay">
            <div className="modal-container">
              <div className="modal-content">
                <p>Enter a name for your new plan:</p>
                <input
                  type="text"
                  placeholder="Plan name"
                  value={customPlanName}
                  onChange={(e) => setCustomPlanName(e.target.value)}
                />
                <StyledButton color="#fdb515" onClick={handleConfirmCreatePlan}>Create</StyledButton>
                <StyledButton color="#fdb515" onClick={() => setIsCreatePlanModalVisible(false)}>Cancel</StyledButton>
              </div>
            </div>
          </div>
        )}


      </div>
    </StyledContainer>
  );
};

export default MakePlan;
