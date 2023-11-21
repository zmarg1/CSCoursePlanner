import React, { useState, useEffect } from 'react';
import { useUser } from '@clerk/clerk-react';

interface PlanFromServer {
  plan_id: string;
  plan_name: string;
  // Add other properties as needed from your server response
}

interface Course {
  course_id: number;
  course_num: string;
  course_title: string;
  credits: number;
  subject_code: string;
}

interface Plan {
  id: string;
  name: string;
}

interface CourseData {
  [year: string]: {
    [term: string]: Course[];
  };
}

const ViewUserPlan: React.FC = () => {
  const { user } = useUser();
  const [courses, setCourses] = useState<CourseData>({});
  const [plans, setPlans] = useState<Plan[]>([]);
  const [selectedPlanId, setSelectedPlanId] = useState('');
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

      const response = await fetch(`http://127.0.0.1:5000/user/plan/view-all-plans/${email}`);
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

  const fetchUserPlan = async (planId: string) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/user/plan/view-plan/${user?.emailAddresses[0]?.emailAddress}/${planId}`);
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
    setSelectedPlanId(planId);
    if (planId) {
      fetchUserPlan(planId);
    }
  };

  return (
    <div>
      <h2>User Plan</h2>
      {error && <p>Error: {error}</p>}
      <select value={selectedPlanId} onChange={handlePlanSelection}>
        <option value="">Select a Plan</option>
        {plans.map(plan => (
          <option key={plan.id} value={plan.id}>{plan.name}</option>
        ))}
      </select>

      <div>
        {Object.entries(courses).map(([year, terms]) => (
          <div key={year}>
            {Object.entries(terms).map(([term, coursesList]) => (
              <div key={term}>
                <h3>{year} - {term}</h3>
                <ul>
                  {Array.isArray(coursesList) && coursesList.map((course, index) => (
                    <li key={index}>
                      <strong>{course.course_title}</strong> - {course.subject_code} {course.course_num}, {course.credits} credits
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ViewUserPlan;

