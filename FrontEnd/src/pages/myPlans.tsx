import React, { useState, useEffect } from 'react';
import { useUser } from '@clerk/clerk-react';
import { StyledButton } from '../common/Button/styles';
import { StyledSelect } from '../common/select/styles';
import jsPDF from 'jspdf';



interface PlanFromServer {
  plan_id: number;
  plan_name: string;
  plan_num: number;
  user_id: string;
}

interface Course {
  course_id: number;
  course_num: string;
  course_title: string;
  credits: number;
  subject_code: string;
}

interface Plan {
  id: number;
  name: string;
}

interface CourseData {
  [year: string]: { [term: string]: Course[]; };
}

const ViewUserPlan: React.FC = () => {
  const { user } = useUser();
  const [courses, setCourses] = useState<CourseData>({});
  const [plans, setPlans] = useState<Plan[]>([]);
  const [selectedPlanId, setSelectedPlanId] = useState(Number);
  const [selectedPlanName, setSelectedPlanName] = useState('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetchPlans();
  }, [user]);

  const fetchPlans = async () => {
    try {
      const email = user?.emailAddresses[0]?.emailAddress;
      if (!email) {
        throw new Error('User email is not available');
      }

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
      setPlans(plansData.map(plan => ({
        id: plan.plan_id,
        name: plan.plan_name
      })));
    } catch (error: any) {
      setError(error.message);
      console.error('Error fetching plans:', error);
    }
  };

  const fetchUserPlan = async (planId: number) => {
    try {
      const email = user?.emailAddresses[0]?.emailAddress;
      const response = await fetch(`http://127.0.0.1:5000/user/plan/view-plan/${email}/${planId}`);

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      console.log(data);
      setCourses(data);

    } catch (error: any) {
      setError(error.message);
      console.error('Error fetching user plan:', error);
    }
  };

  const handlePlanSelection = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const planId = event.target.value;
    const parsedPlanId = parseInt(planId, 10);
    setSelectedPlanId(parsedPlanId);

    const selectedPlan = plans.find(plan => plan.id === parsedPlanId);

    if (selectedPlan) {
      setSelectedPlanName(selectedPlan.name);
      fetchUserPlan(parsedPlanId);
    }
  };


  // Function to create the pdf once the download button is clicked
  const generatePDF = () => {

    const doc = new jsPDF();

    let y = 10; // sets the vertical positioning

    // Iterate through each year of the courses map
    Object.entries(courses).forEach(([year, terms]) => {

      // iterates over each term in a year
      Object.entries(terms).forEach(([term, coursesList]) => {

        // Set the font size for the term, year headers
        doc.setFontSize(14);

        // prints the year and term format
        doc.text(`${year} - ${term}`, 10, y);

        // now add space before the courses
        y += 10;

        // font size for courses information
        doc.setFontSize(10);

        // Iterates over each course in the semester
        coursesList.forEach((course, index) => {

          // prints the course information
          const text = `${course.course_title} - ${course.subject_code} ${course.course_num}, ${course.credits} credits`;

          // finally add all the text to pdf
          doc.text(text, 15, y);

          // add more space between each course
          y += 10;
        });

        // andd more space between different terms
        y += 5;
      });
    });


    // saves the pdf to specified name
    doc.save(`${selectedPlanName}.pdf`);
  };

  return (
    <div>
      <h2>View Plan</h2>
      {error && <p>Error: {error}</p>}
      <StyledSelect
        value={selectedPlanId}
        onChange={handlePlanSelection}
        required
        color="#fdb515"
      >
        <option value="">Select a Plan</option>
        {plans.map(plan => (
          <option key={plan.id} value={plan.id}>{plan.name}</option>
        ))}
      </StyledSelect>

      <div style={{ margin: '10px' }}>
        {Object.entries(courses).map(([year, terms]) => (
          <div key={year} style={{ marginBottom: '1px', paddingLeft: '1px' }}>
            {Object.entries(terms).map(([term, coursesList]) => (
              <div key={term}>
                <h6 style={{ color: '#333' }}>{year} - {term}</h6>
                <ul style={{ listStyleType: 'none', paddingLeft: '5px' }}>
                  {Array.isArray(coursesList) && coursesList.map((course, index) => (
                    <li key={index} style={{ marginBottom: '10px' }}>
                      <strong>{course.course_title}</strong> - {course.subject_code} {course.course_num}, {course.credits} credits
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ))}
      </div>

      <StyledButton 
      color="#fdb515"
      onClick={generatePDF}>Download PDF</StyledButton>
    </div>
  );
};

export default ViewUserPlan;

