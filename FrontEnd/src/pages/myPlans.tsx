import React, { useState, useEffect } from 'react';
import { useUser } from '@clerk/clerk-react';
import { StyledButton } from '../common/Button/styles';
import { StyledSelect } from '../common/select/styles';
import jsPDF from 'jspdf';
import '../common/Modal/modal.css';
import { SmallerStyledButton } from '../common/Button/styles';
import '../common/PlanStyling/Plan.css'
import { useNavigate } from 'react-router-dom';
import '../common/PlanStyling/Plan.css';
import { notification } from "antd";
import { StyledContainer } from '../common/Container/styles';

const URL = `http://127.0.0.1:5000`

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
  const [isCourseModalOpen, setIsCourseModalOpen] = useState(false);
  const [isPlanModalOpen, setIsPlanModalOpen] = useState(false);
  const [courseToDelete, setCourseToDelete] = useState<CourseToDelete | null>(null);
  const [planToDelete, setPlanToDelete] = useState<number | null>(null);

  useEffect(() => {
    if (isCourseModalOpen || isPlanModalOpen) {
      document.body.classList.add('no-scroll');
    } else {
      document.body.classList.remove('no-scroll');
    }
  }, [isCourseModalOpen || isPlanModalOpen]);
  

  const openDeletionNotification = (title: string) => {
      notification["success"]({
      message: "Plan Deleted Successfully",
      description: `Your plan "${title}" has been successfully deleted.`,
      duration: 10,
    });
  };

  const confirmPlanDelete = (planId: number) => {
    setPlanToDelete(planId); // Set the plan to delete
    setIsPlanModalOpen(true); // Open the confirmation modal
  };

  const handleDeletePlanConfirmation = () => {
    if (planToDelete !== null) {
      removePlan(planToDelete); // Call the function to remove the plan
    }
    setIsPlanModalOpen(false); // Close the confirmation modal
  };

  const removePlan = async (planId: number) => {
    const email = user?.emailAddresses[0]?.emailAddress;
    if (!email) {
      setError('User email is not available');
      return;
    }

    try {
      const response = await fetch(`${URL}/user/plan/delete-plan/${email}/${planId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const responseData = await response.json();
      if (responseData.Success) {
        console.log(responseData.Success);
        setPlans(prevPlans => prevPlans.filter(plan => plan.id !== planId));
        const deletedPlanName = plans.find(plan => plan.id === planId)?.name || "Unknown Plan";
        openDeletionNotification(deletedPlanName);
      } 
      else {
        throw new Error(responseData.Failed || 'Failed to delete the plan');
      }
      
    } catch (error: any) {
      setError(error.message);
      console.error('Error removing plan:', error);
    }
  };

  const isPlanEmpty = () => {
    return Object.values(courses).every(term => Object.values(term).every(courseList => courseList.length === 0));
  };

  const handleAddMoreClick = () => {
    navigate('/user/plan/make-plan');
  };


  const confirmDelete = (courseId: number, planId: number, year: string, term: string) => {
    setCourseToDelete({ courseId, planId, year, term }); // Ensure this matches the CourseToDelete type
    setIsCourseModalOpen(true);
  };

  const handleDeleteConfirmation = () => {
    if (courseToDelete) {
      removeCourseFromPlan(courseToDelete.courseId, courseToDelete.planId, courseToDelete.year, courseToDelete.term);
    }
    setIsCourseModalOpen(false);
  };

  const removeCourse = (year: string, term: string, courseId: number) => {
    setCourses(prevCourses => {
      // Filter out the removed course
      const updatedCourses = prevCourses[year][term].filter(course => course.course_id !== courseId);

      // Check if the term is empty after removing the course
      if (updatedCourses.length === 0) {
        // If empty, remove the term
        const { [term]: removedTerm, ...remainingTerms } = prevCourses[year];
        return {
          ...prevCourses,
          [year]: remainingTerms
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
      const response = await fetch(`${URL}/user/plan/delete-course-from-plan/${email}/${planId}/${courseId}`, {
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
      const response = await fetch(`${URL}/user/plan/view-plan/${email}/${planId}`);

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
    <StyledContainer className='myPlan'>
      <h2>View Plan</h2>
      {error && <p>Error: {error}</p>}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}></div>
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


      {isPlanEmpty() ? (
        <div style={{ textAlign: 'center', marginTop: '3%' }}>
          <p className='Empty-Plan'>Your plan is currently empty.</p>
          <p className='Empty-Plan'>Select a plan to view or add more classes!!!</p>
          <img className='Empty-Picture' src="/img/Retriever_sad.png" alt="Empty Plan" />
        </div>
      ) : (
        <div style={{ margin: '1%' }}>
          {Object.entries(courses).map(([year, terms]) => (
            <div key={year} className="terms-container">
              {Object.entries(terms).filter(([_, coursesList]) => coursesList.length > 0)
                .map(([term, coursesList]) => (
                  <div key={term} className="term">
                    <h6 style={{ color: '#333' }}>{year} - {term}</h6>
                    <ul style={{ listStyleType: 'none', paddingLeft: '1%' }}>
                      {coursesList.map((course, index) => (
                        <li key={index} style={{ display: 'flex', alignItems: 'center', marginBottom: '2%', marginRight:'3%' }}>
                          <div style={{ flex: 0.9, marginRight: '2%' }}>
                            <strong>{course.course_title}:</strong>
                            <div style={{ flex: 1, marginRight: '2%' }}>
                              <strong>{course.subject_code} {course.course_num}, {course.credits} credits</strong>
                            </div>
                          </div>
                          <div style={{ marginLeft: '20%' }}> {/* Padding between description and button */}
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
      )}
      <div className='button-container-myPlan' style={{ marginTop: '5%' }}>
        <StyledButton color="#fdb515" onClick={generatePDF}>Download PDF</StyledButton>
        <StyledButton color="#fdb515" onClick={handleAddMoreClick}>Add More Classes</StyledButton>
        <StyledButton
          color="#fdb515"
          onClick={() => selectedPlanId && confirmPlanDelete(selectedPlanId)} style={{ marginTop: '1%' }}>Remove Plan</StyledButton>
        <ConfirmationModal
          isOpen={isCourseModalOpen}
          onClose={() => setIsCourseModalOpen(false)}
          onConfirm={handleDeleteConfirmation}
          message="Are you sure you want to delete this course?"
        />
        <ConfirmationModal
          isOpen={isPlanModalOpen}
          onClose={() => setIsPlanModalOpen(false)}
          onConfirm={planToDelete ? handleDeletePlanConfirmation : handleDeleteConfirmation}
          message="Are you sure you want to delete this plan?"
        />
      </div>
    </StyledContainer>
  );
};

export default ViewUserPlan;

