import React, { useState, useEffect } from 'react';
import { StyledSelect } from '../common/select/styles';
import { StyledButton } from '../common/Button/styles';
import { StyledLabel } from '../common/Label';
import { supabase } from '../utils/supabaseClient';
import { useUser } from '@clerk/clerk-react';

interface CourseFromServer {
  course_id: number;
  course_num: string;
  course_title: string;
  credits: number;
  subject_code: string;
}

interface Course {
  id: number;
  code: string;
  name: string;
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


const MakePlan: React.FC = () => {
  const { user } = useUser();
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState('');
  const [selectedCourseTitle, setSelectedCourseTitle] = useState('');
  const [semesters, setSemesters] = useState<Semester[]>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [selectedSemesterId, setSelectedSemesterId] = useState('');
  const [selectedPlanId, setSelectedPlanId] = useState('');
  // const [userPlan, setUserPlan] = useState<PlanItem[]>([]);

  useEffect(() => {

    const fetchCourses = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/user/view-all-courses', {
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
        const sortedCoursesData = coursesData.sort((a: CourseFromServer, b: CourseFromServer) => {
          const courseNumA = parseInt(a.course_num, 10);
          const courseNumB = parseInt(b.course_num, 10);
          return courseNumA - courseNumB;
        });

        setCourses(sortedCoursesData.map((course: CourseFromServer) => ({
          id: course.course_id,
          code: `${course.subject_code} ${course.course_num}: `,
          name: `${course.course_title}`
        })));
      } catch (error) {
        console.error('There has been a problem with your fetch operation:', error);
      }
    };

    // const fetchPlan = async () => {
    //   try {
    //     const response = await fetch('http://127.0.0.1:5000/user/plan/get-plan', {
    //       method: 'GET',
    //       headers: {
    //         'Content-Type': 'application/json',
    //         // Include other headers as necessary
    //       },
    //     });

    //     if (!response.ok) {
    //       throw new Error(`HTTP error! status: ${response.status}`);
    //     }

    //     const planData = await response.json();
    //     // Assuming the server returns an array of PlanItems
    //     setUserPlan(planData);
    //   } catch (error) {
    //     console.error('There was an error fetching the plan:', error);
    //   }
    // }


    const fetchSemesters = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/user/view-all-semesters', {
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

    // Fetch User Data from Supabase
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

    const fetchPlans = async () => {
      try {
        const email = user?.emailAddresses
        const response = await fetch(`http://127.0.0.1:5000/user/plan/view-all-plans/${email}`, {
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

    fetchPlans();
    fetchCourses();
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

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json()
      if(data.Success){
        console.log(data)
      }
      if(data.Failed){
        console.log(data)
      }

      // Update the user's plan state
      // setUserPlan([...userPlan, { courseId: selectedCourseId, semesterId: parseInt(selectedSemesterId, 10) }]);

    } catch (error) {
      console.error('Error adding class to plan:', error);
    }

    const handleMakePlan = async () => {
      try {
        const response = await fetch('/user/plan/make-plan', {
          method: 'POST',
          // Include headers and credentials as necessary for your setup
        });
        const result = await response.text();
        alert(result); // Or handle the success/failure in a more robust way
      } catch (error) {
        console.error('There was an error making the plan:', error);
      }
    };
  };


  const handleCourseSelection = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCourseTitle(event.target.title);
    console.log('Added Class Title:', selectedCourseTitle);
    setSelectedCourseId(event.target.value);
    console.log('Added Class ID:', selectedCourseId);
  };

  const handleSemesterSelection = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedSemesterId(event.target.value);
  };

  const handlePlanSelection = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedPlanId(event.target.value);
  };


  return (
    <div className="make-plan">
      <h2>Make Your Plan</h2>
      <form onSubmit={handleAddClass}>
        <div>
          <StyledLabel htmlFor="semester-dropdown">Select a term:</StyledLabel>
          <StyledSelect
            id="semester-dropdown"
            value={selectedSemesterId}
            onChange={handleSemesterSelection}
            required
            color="#fdb515"
          >
            <option key="" value="">Select a term</option>
            {semesters.map((semester, index) => (
              <option key={semester.id || index} value={semester.id}>
                {semester.name}
              </option>
            ))}
          </StyledSelect>
        </div>
        <div>
          <StyledLabel htmlFor="course-dropdown">Select a class:</StyledLabel>
          <StyledSelect
            id="course-dropdown"
            value={selectedCourseId}
            onChange={handleCourseSelection}
            required
            color="#fdb515"
          >
            <option key="" value="" title="">Select a class</option>
            {courses.map((course) => (
              <option key={course.id} value={course.id} title={course.name}>
                {course.code}{course.name}
              </option>
            ))}
          </StyledSelect>
        </div>
        <div>
          <StyledLabel htmlFor="plan-dropdown">Select a plan:</StyledLabel>
          <StyledSelect
            id="plan-dropdown"
            value={selectedPlanId}
            onChange={handlePlanSelection}
            required
            color="#fdb515"
          >
            <option key="" value="">Select a plan</option>
            {plans.map((plan) => (
              <option key={plan.id} value={plan.id}>
                {plan.name} {/* Adjust this to display relevant plan details */}
              </option>
            ))}
          </StyledSelect>
        </div>
        <StyledButton type="submit">Add Class</StyledButton>
      </form>
    </div>
  );
};

export default MakePlan;