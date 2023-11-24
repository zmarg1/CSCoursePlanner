import React, { useState, useEffect } from 'react';
import { useUser } from '@clerk/clerk-react';
import { StyledButton } from '../common/Button/styles';
import { StyledSelect } from '../common/select/styles';
import jsPDF from 'jspdf';
import '../common/Modal/modal.css';
import { SmallerStyledButton } from '../common/Button/styles';
import '../common/PlanStyling/Plan.css'
import { useNavigate } from 'react-router-dom';



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

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  message: string;
}

interface CourseData {
  [year: string]: { [term: string]: Course[]; };
}

interface CourseToDelete {
  courseId: number;
  planId: number;
  year: string;
  term: string;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({ isOpen, onClose, onConfirm, message }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container"> 
        <img src="/img/Retriever_clipart.png" alt="Left Side" className="modal-side-image" />
        <div className="modal-content">
          <p>{message}</p>
          <SmallerStyledButton
            color="#fdb515"
            onClick={onConfirm}>Confirm
          </SmallerStyledButton>
          <SmallerStyledButton
            color="#fdb515"
            onClick={onClose}>Cancel
          </SmallerStyledButton>
        </div>
        <img src="/img/Retriever_clipart.png" alt="Right Side" className="modal-side-image" />
      </div>
    </div>
  );
};




const ViewUserPlan: React.FC = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [courseToDelete, setCourseToDelete] = useState<CourseToDelete | null>(null);

  const handleAddMoreClick = () => {
    navigate('/user/plan/make-plan');
  };


  const confirmDelete = (courseId: number, planId: number, year: string, term: string) => {
    setCourseToDelete({ courseId, planId, year, term }); // Ensure this matches the CourseToDelete type
    setIsModalOpen(true);
  };

  const handleDeleteConfirmation = () => {
    if (courseToDelete) {
      removeCourseFromPlan(courseToDelete.courseId, courseToDelete.planId, courseToDelete.year, courseToDelete.term);
    }
    setIsModalOpen(false);
  };

  const removeCourse = (year: string, term: string, courseId: number) => {
    setCourses(prevCourses => {
      // Filter out the removed course
      const updatedCourses = prevCourses[year][term].filter(course => course.course_id !== courseId);

      // Check if the term is empty after removing the course
      if (updatedCourses.length === 0) {
        // If empty, remove the term
        const { [term]: removedTerm, ...updatedTerms } = prevCourses[year];
        return {
          ...prevCourses,
          [year]: updatedTerms
        };
      } else {
        // If not empty, update the term with the remaining courses
        return {
          ...prevCourses,
          [year]: {
            ...prevCourses[year],
            [term]: updatedCourses
          }
        };
      }
    });
  };

  const removeCourseFromPlan = async (courseId: number, planId: number, year: string, term: string) => {
    const email = user?.emailAddresses[0]?.emailAddress;
    if (!email) {
      setError('User email is not available');
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:5000/user/plan/delete-course-from-plan/${email}/${planId}/${courseId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Optionally handle the response if needed
      const responseData = await response.json();
      console.log(responseData);

      // Update local state to reflect the change
      removeCourse(year, term, courseId);

    } catch (error: any) {
      setError(error.message);
      console.error('Error removing course from plan:', error);
    }
  };


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

  const generatePDF = () => {
    const doc = new jsPDF();
    let y = 20; // Starting vertical position
  
    const headers = ["Course Title", "Subject Code", "Course Num", "Credits"];
    const columnWidths = [90, 30, 40, 30]; // Adjust as needed
  
    doc.setFont("helvetica", "bold");
  
    const splitText = (text: string, maxWidth: number): string[] => {
      // This function will split the text into lines based on the maxWidth
      return doc.splitTextToSize(text, maxWidth);
    };
  
    Object.entries(courses).forEach(([year, terms]) => {
      Object.entries(terms).forEach(([term, coursesList]) => {
        let termTotalCredits = 0;
  
        doc.setTextColor(0, 0, 255); // Blue color for headers
        doc.setFontSize(14);
        doc.text(`${year} - ${term}`, 10, y);
        y += 10;
  
        doc.setTextColor(0, 0, 0); // Black color for text
        doc.setFontSize(10);
        let x = 10; // Starting horizontal position
        headers.forEach((header, index) => {
          doc.text(header, x, y);
          x += columnWidths[index];
        });
        y += 10;
  
        coursesList.forEach((course) => {
          let x = 10; // Reset horizontal position
          const courseCredits = course.credits || 0;
          const splitCourseTitle = splitText(course.course_title, columnWidths[0]);
          const lineHeight = 7; // Adjust line height as needed
          let maxY = y;
  
          // Print Course Title (potentially multiple lines)
          splitCourseTitle.forEach((line: string) => {
            doc.text(line, x, maxY);
            maxY += lineHeight;
          });
  
          // Print other course details (aligned with the first line of the title)
          doc.text(course.subject_code, x + columnWidths[0], y);
          doc.text(course.course_num, x + columnWidths[0] + columnWidths[1], y);
          doc.text(courseCredits.toString(), x + columnWidths[0] + columnWidths[1] + columnWidths[2], y);
  
          y = Math.max(maxY, y + lineHeight); // Move to next row, considering multi-line titles
  
          // Add to term total credits
          if (course.credits != null) {
            termTotalCredits += course.credits;
          }
        });
  
        doc.setFontSize(12);
        doc.setTextColor(255, 0, 0); // Red color for total credits
        doc.text(`Total Credits for ${term}: ${termTotalCredits}`, 10, y);
        y += 15; // Space after each term's total credits
      });
    });
  
    doc.save(`${selectedPlanName}.pdf`);
  };
  
  
  
  
  

  return (
    <div className='myPlan'>
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
          <div key={year} className="terms-container">
            {Object.entries(terms).map(([term, coursesList]) => (
              <div key={term} className="term">
                <h6 style={{ color: '#333' }}>{year} - {term}</h6>
                <ul style={{ listStyleType: 'none', paddingLeft: '5px' }}>
                  {coursesList.map((course, index) => (
                    <li key={index} style={{ display: 'flex', alignItems: 'left', marginBottom: '10px' }}>
                      <div style={{ flex: 0.36, marginRight: '10px' }}>
                        <strong>{course.course_title}</strong> - {course.subject_code} {course.course_num}, {course.credits} credits
                      </div>
                      <div style={{ marginLeft: '50px' }}> {/* Padding between description and button */}
                        <SmallerStyledButton
                          color="#fdb515"
                          onClick={() => confirmDelete(course.course_id, selectedPlanId, year, term)}>Remove
                        </SmallerStyledButton>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ))}
      </div>
      <div className='button-container' style={{ marginTop: '20px' }}>
        <StyledButton color="#fdb515" onClick={generatePDF}>Download PDF</StyledButton>
        <StyledButton color="#fdb515" onClick={handleAddMoreClick}>Add More Classes</StyledButton>
        <ConfirmationModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onConfirm={handleDeleteConfirmation}
          message="Are you sure you want to delete this course?"
        />
      </div>
    </div>
  );
};

export default ViewUserPlan;

