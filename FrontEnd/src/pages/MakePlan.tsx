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


// const Freshman_Status = "/img/Freshman_Status-removebg-preview.png"
// const Sophomore_Status = "/img/Sophomore_Status-removebg-preview.png"
// const Junior_Status = "/img/Junior_Status-removebg-preview.png"
// const Senior_Status = "/img/Senior_Status-removebg-preview.png"
const URL = `http://127.0.0.1:5000`

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

  const determineStudentStatus = (semesterCount: number) => {
    if (semesterCount < 2) return 'Freshman';
    if (semesterCount < 4) return 'Sophomore';
    if (semesterCount < 6) return 'Junior';
    return 'Senior';
  };

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

      // Assuming you want to set the plan IDs in a state
      setPlans(plansData.map(plan => ({
        id: plan.plan_id,
        name: `${plan.plan_name}`
        // You can add more fields if you have additional data for each plan
      })));
    } catch (error) {
      console.error('Error fetching plans:', error);
    }
  };

  const handleCreatePlan = async () => {
    // Ensure that the user's email is available
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
        // You can send additional data in the request body, if necessary
        // body: JSON.stringify({ additionalData: 'value' })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Plan creation result:', result);

      if (result.Success){
        openPlanNotificationSuccess(result.Success);
      }
      else{
        openPlanNotificationFailed(result.Failed);
      }
      await fetchPlans();

      // You can add additional logic here to handle the response,
      // such as navigating to a different page, updating the state, etc.

    } catch (error) {
      console.error('There was an error creating the plan:', error);
    }
  };

  const fetchCourses = async (plan_id: string) => {
    try {
      const email = user?.emailAddresses
      const response = await fetch(`${URL}/user/view-all-courses/${email}/${plan_id}`, {
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
    } catch (error) {
      console.error('There has been a problem with your fetch operation:', error);
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
    try{
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

      if (!data.Failed){
        console.log(data);
        setSemesterCourses(data);
      }

    }
    catch(error){
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
    fetchCourses("-1") //Default -1 to show all courses
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

      if (result.Success){
        openAddClassNotificationSuccess(result.Success)
        viewSemesterCourses(selectedPlanId, selectedSemesterId);
        fetchCourses(selectedPlanId) 
      }
      else{
        openAddClassNotificationFailed(result.Failed)
      }

      // Update the user's plan state
      // setUserPlan([...userPlan, { courseId: selectedCourseId, semesterId: parseInt(selectedSemesterId, 10) }]);

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
    if (selectedPlanId){
      viewSemesterCourses(selectedPlanId, event.target.value);
    }

  };

  const handlePlanSelection = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedPlanId(event.target.value);
    if (selectedSemesterId){
      viewSemesterCourses(event.target.value, selectedSemesterId);
    }
    fetchCourses(event.target.value);
  };

  return (
    <StyledContainer className="make-plan">
      <div>
      <h2>Make Your Plan</h2>
      </div>
      {/* <div style={{ flex: 1, paddingLeft: '20px' }}> 
        {studentStatus === 'Freshman' && <img src={Freshman_Status} alt="Freshman" />}
        {studentStatus === 'Sophomore' && <img src={Sophomore_Status} alt="Sophomore" />}
        {studentStatus === 'Junior' && <img src={Junior_Status} alt="Junior" />}
        {studentStatus === 'Senior' && <img src={Senior_Status} alt="Senior" />}
      </div> */}
      <div>
      <StyledButton color="#fdb515" onClick={handleCreatePlan} style={{ marginBottom: '30px'}}>Create Plan</StyledButton>
      </div>

      <form onSubmit={handleAddClass}>
        <div>

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
        
        </div>
        
        <div className='button-container-makePlan' style={{ marginTop: '50px' }}> {/* Increased space above the buttons */}
          <StyledButton color="#fdb515" type="submit">Add Course</StyledButton>
          <StyledButton color="#fdb515" onClick={handleViewPlanClick}>View Plans</StyledButton>
        </div>
      </form>

        <div style={{ margin: '15px' }}>
          {Object.entries(semesterCourses).map(([year, terms]) => (
            <div key={year} className="terms-container">
              {Object.entries(terms).filter(([_, coursesList]) => coursesList.length > 0)
                .map(([term, coursesList]) => (
                  <div key={term} className="term">
                    <h6 style={{ color: '#333' }}>{year} - {term}</h6>
                    <ul style={{ listStyleType: 'none', paddingLeft: '5px' }}>
                      {coursesList && Array.isArray(coursesList) && coursesList.map((course, index) => (
                        <li key={index} style={{ display: 'flex', alignItems: 'left', marginBottom: '10px' }}>
                          <div>
                            <div style={{ flex: 0.40, marginRight: '10px' }}>
                              <strong>{course.course_title} - </strong>
                            </div>
                            <strong>{course.subject_code} {course.course_num}, {course.credits} credits </strong>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
            </div>
          ))}
        </div>

    </StyledContainer>
  );
};

export default MakePlan;