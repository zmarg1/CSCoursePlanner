import React, { useState, useEffect } from 'react';
import { StyledSelect } from '../common/select/selectStyles';
import { StyledButton } from '../common/Button/custButtonStyles';
import { StyledLabel } from '../common/Label/customLabel';
import { useUser } from '@clerk/clerk-react';
import '../common/PlanStyling/Plan.css';
import { useNavigate } from 'react-router-dom';
import { notification } from "antd";
import { StyledContainer, ButtonContainerMakePlan } from '../common/Container/custContainerStyles';

const URL = process.env.REACT_APP_BACKEND_URL || 'http://127.0.0.1:5000';

// Typescript interfaces

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

interface Prereq {
  [req: string]: Course[];
}

const MakePlan: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useUser();

  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState('');
  const [selectedCourseTitle, setSelectedCourseTitle] = useState('');
  const [selectedCurseCode, setSelectedCouresCode] = useState('')

  const [semesters, setSemesters] = useState<Semester[]>([]);
  const [selectedSemesterId, setSelectedSemesterId] = useState('');

  const [plans, setPlans] = useState<Plan[]>([]);
  const [selectedPlanId, setSelectedPlanId] = useState('');

  const [isCreatePlanModalVisible, setIsCreatePlanModalVisible] = useState(false);
  const [customPlanName, setCustomPlanName] = useState('');


  const handleConfirmCreatePlan = async () => {
    setIsCreatePlanModalVisible(false);

    const planName = customPlanName.trim();

    const userEmail = user?.emailAddresses[0]?.emailAddress;
    if (!userEmail) {
      console.error('User email is not available');
      return;
    }

    try {
      console.log("Plan Name: ", planName)
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
      console.log('Plan creation result:', result.result);

      if (result.status == "Failed") {
      } else {
        openPlanNotificationFailed(result.result);
      }

      await fetchPlans();
      setCustomPlanName(''); // Reset custom plan name after the operation

    } catch (error) {
      console.error('There was an error creating the plan:', error);
    }
  };


  // const renamePlan = async (userEmail: string, planId: number, newName: string) => {
  //   try {
  //     // Construct the correct URL with path parameters
  //     const url = `${URL}/user/plan/rename-plan/${userEmail}/${planId}`;

  //     const response = await fetch(url, {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json'
  //       },
  //       body: JSON.stringify({ new_name: newName }) // Include new_name in the request body
  //     });

  //     if (!response.ok) {
  //       throw new Error(`HTTP error! status: ${response.status}`);
  //     }

  //     const result = await response.json();
  //     if (result.status == "Success") {
  //       openPlanNotificationSuccess(`Plan renamed to "${newName}" successfully.`);
  //     } else {
  //       openPlanNotificationFailed(result.result);
  //     }
  //   } catch (error) {
  //     console.error('Error renaming plan:', error);
  //   }
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
      description: `${courseTitle}`,
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
      const planResult = await response.json()

      if (planResult.status == "Success") {
        const plansData: PlanFromServer[] = planResult.result;
        const sortedPlans = plansData.sort((a, b) => a.plan_name.localeCompare(b.plan_name));

        // Assuming you want to set the plan IDs in a state
        setPlans(sortedPlans.map(plan => ({
          id: plan.plan_id,
          name: `${plan.plan_name}`
          // You can add more fields if you have additional data for each plan
        })));

      }
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
      const response = await fetch(`${URL}/user/view-term-courses/${email}/${plan_id}/${sem_id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const coursesResponse = await response.json();

      if (coursesResponse.status == "Failed") {
        console.error('Error parsing JSON:', coursesResponse.result);
        const rawResponse = await response.text();
        console.log('Raw response:', rawResponse);
        return;
      }

      const coursesData = coursesResponse.result
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

      const semResult = await response.json();
      const semestersData: SemesterFromServer[] = semResult.result;

      setSemesters(semestersData.map(semester => ({
        id: semester.semester_id,
        name: `${semester.term} ${semester.year}`
      })));
    } catch (error) {
      console.error('Error fetching semesters:', error);
    }
  };

  const [showPreview, setShowPreview] = useState(false);
  const [semesterCourses, setSemesterCourses] = useState<CourseData>({});

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
      const coursesResult = await response.json();

      if (coursesResult.status == "Success") {
        console.log("Semester Courses Data:", coursesResult.result);
        setSemesterCourses(coursesResult.result);
        setShowPreview(true)
      }
      else {
        setShowPreview(false)
      }

    }
    catch (error) {
      console.error('Error viewing semester:', error);
    }
  };

  const [prereqCourses, setPrereqCourses] = useState<Prereq>({});
  const [showPrereqs, setShowPrereqs] = useState(false);

  const viewPrereqs = async (crs_id: string) => {
    try {
      const response = await fetch(`${URL}/user/course/view-prereqs/${crs_id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const prereqsResult = await response.json();

      if (prereqsResult.status == "Failed") {
        console.log(prereqsResult.result)
        setShowPrereqs(false)
      }
      else {
        console.log(`Course Prereqs`, prereqsResult.result);
        setPrereqCourses(prereqsResult.result)
        setShowPrereqs(true)
      }

    }
    catch (error) {
      console.error('Error viewing semester:', error);
    }
  }

  useEffect(() => {
    fetchPlans();
    fetchSemesters();
  }, [user]);

  const handleAddClass = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();  // Prevent the form from causing a page reload
    try {
      const email = user?.emailAddresses
      const response = await fetch(`${URL}/user/plan/add-course-to-plan/${email}/${selectedPlanId}/${selectedCourseId}/${selectedSemesterId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json()

      if (result.status == "Success") {
        openAddClassNotificationSuccess(result.result)
        viewSemesterCourses(selectedPlanId, selectedSemesterId);
        fetchCourses(selectedPlanId, selectedSemesterId)
      }
      else {
        openAddClassNotificationFailed(result.result)
      }

    } catch (error) {
      console.error('Error adding class to plan:', error);
    }
  };

  const handleCourseSelection = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOption = event.target.options[event.target.selectedIndex];
    const selectedTitle = selectedOption.text;
    const selectedCode = selectedOption?.dataset.subjCode || "";
    setSelectedCourseTitle(selectedTitle);
    setSelectedCouresCode(selectedCode);
    setSelectedCourseId(event.target.value);
    viewPrereqs(event.target.value);
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
                <option
                  key={course.course_id} value={course.course_id} title={course.course_title}
                  data-subj-code={`${course.subject_code} ${course.course_num}`}
                >
                  {course.subject_code} {course.course_num}: {course.course_title} {course.credits}cr
                </option>
              ))}
            </StyledSelect>
            <ButtonContainerMakePlan>
              <StyledButton color="#fdb515" onclick={handleAddClass} type="submit">Add Course</StyledButton>
              <StyledButton color="#fdb515" onClick={handleViewPlanClick}>View Plans</StyledButton>
            </ButtonContainerMakePlan>
          </form>
        </div>

        <div style={{ textAlign: 'center' }}>
          {showPreview && (
            <div className="terms-section">
              {Object.entries(semesterCourses).map(([year, terms]) => (
                Object.entries(terms).filter(([_, coursesList]) => coursesList.length > 0)
                  .map(([term, coursesList]) => (
                    <div key={term} className="term">
                      <h6 style={{ color: '#333', textAlign: 'center' }}>{term} {year}</h6>
                      <ul style={{ listStyleType: 'none', paddingLeft: '5px' }}>
                        {coursesList.map((course, index) => (
                          <li key={index} style={{ marginBottom: '10px' }}>
                            <div style={{ textAlign: 'center' }}>
                              <strong>{course.course_title} - {course.subject_code} {course.course_num}, {course.credits} credits</strong>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))
              ))}
            </div>)}

          {showPrereqs && (
            <div className="prereqs-section">
              <p style={{ fontWeight: 'bold', textAlign: 'center' }}>{selectedCurseCode} Prerequisites</p>
              {Object.entries(prereqCourses).map(([req, courses], index) => (
                <div key={req} className="term">
                  {index > 0 && <p style={{ color: '#333' }}> and </p>}
                  <ul style={{ listStyleType: 'none', paddingLeft: '5px' }}>
                    {courses.map((course, courseIndex) => (
                      <li key={course.course_id} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '10px' }}>
                        <div style={{ textAlign: 'center' }}>
                          <strong>{course.course_title} - {course.subject_code} {course.course_num}</strong>
                        </div>
                        {courseIndex < courses.length - 1 && (
                          <div style={{ fontWeight: 'bold', textAlign: 'center', width: '100%' }}> or </div>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )

          }
        </div>

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
