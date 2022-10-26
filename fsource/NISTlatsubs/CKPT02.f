      SUBROUTINE CKPT02(IFLAG2)
      COMMON /DOTP/ S11,S22,S33,S23,S13,S12
      COMMON /MATR1/ U1,V1,W1,U2,V2,W2,U3,V3,W3
      COMMON /PROB1/ NTD,IPROB
      COMMON /TYPE/ ITYPE
      COMMON /UNIT2/ IUNITB
C
C
C     SUBROUTINE 'CKPT02' ...
C        CHECK PRINT OUT FOR THE RSS PROGRAM FUNCTION
C
C
C
C     --- IF THE CALL ARGUMENT (IFLAG2) IS GREATER THAN OR EQUAL TO
C         31, IT MUST BE DECODED TO OBTAIN THE NUMBER OF THE SPECIAL
C         CONDITION AND THE 'CALL ARGUMENT' FOR THE OUTPUT
      ICOND = 0
      IF(IFLAG2.GE.31) ICOND = IFLAG2 - 30
      IF(IFLAG2.GE.31) IFLAG2 = 10
C
C     --- GO TO APPROPRIATE SECTION OF OUTPUT
      GO TO (10,20,30,40,50,60,70,80,90,100,110,120,130) IFLAG2
   10 CONTINUE
C
C     *** CALLED FROM 'MNCOND'
C
C     --- WRITE CELL MATRIX AND TRANSFORMATION MATRIX AT BEGINNING OF
C         SUBROUTINE 'MNCOND'
      WRITE(IUNITB,6100) IFLAG2, S11, S22, S33, S23, S13, S12,
     $                   U1, V1, W1, U2, V2, W2, U3, V3, W3
      GO TO 900
   20 CONTINUE
   30 CONTINUE
   40 CONTINUE
C
C     *** CALLED FROM 'MNCOND'
C
C     --- WRITE PRIOR TO CALLS TO 'SHORTV'
C         IFLAG2 = 2    ...   PRIOR TO FIRST CALLS
C         IFLAG2 = 3    ...   PRIOR TO SECOND CALLS
C         IFLAG2 = 4    ...   PRIOR TO THIRD CALLS
      WRITE(IUNITB,6100) IFLAG2
      GO TO 900
   50 CONTINUE
   60 CONTINUE
   70 CONTINUE
C
C     *** CALLED FROM 'MNCOND'
C
C     --- WRITE CELL MATRIX AND TRANSFORMATION MATRIX AT
C         INTERMEDIATE STAGES
C         IFLAG2 = 5 ... AFTER CELL EDGES A AND B HAVE BEEN INTERCHANGED
C         IFLAG2 = 6 ... AFTER CELL EDGES B AND C HAVE BEEN INTERCHANGED
C         IFLAG2 = 7 ... AFTER CALCULATING THE BODY DIAGONAL OF THE CELL
      WRITE(IUNITB,6100) IFLAG2, S11, S22, S33, S23, S13, S12,
     $                   U1, V1, W1, U2, V2, W2, U3, V3, W3
      GO TO 900
   80 CONTINUE
C
C     *** CALLED FROM 'SHORTV'
C
C     --- WRITE CELL MATRIX AND TRANSFORMATION MATRIX AT END
C         OF SUBROUTINE 'SHORTV'
      WRITE(IUNITB,6200) S11, S22, S33, S23, S13, S12,
     $                   U1, V1, W1, U2, V2, W2, U3, V3, W3
      GO TO 900
   90 CONTINUE
C
C     *** CALLED FROM 'NORMAL'
C
C     --- WRITE CELL TYPE, CELL MATRIX, TRANSFORMATION MATRIX
      WRITE(IUNITB,6300) ITYPE, S11, S22, S33, S23, S13, S12,
     $                   U1, V1, W1, U2, V2, W2, U3, V3, W3
      GO TO 900
  100 CONTINUE
C
C     *** CALLED FROM 'SPCON2'
C
C     --- WRITE SPECIAL CONDITION NUMBER, CELL TYPE, CELL MATRIX,
C         TRANSFORMATION MATRIX
      WRITE(IUNITB,6400) ICOND, ITYPE, S11, S22, S33, S23, S13, S12,
     $                   U1, V1, W1, U2, V2, W2, U3, V3, W3
      GO TO 900
  110 CONTINUE
C
C     *** CALLED FROM 'SPCON2'
C
C     --- WRITE CELL MATRIX AND TRANSFORMATION MATRIX AFTER THE
C         TRANSFORMATION TO SATISFY THE SPECIAL CONDITION HAS BEEN
C         APPLIED
      WRITE(IUNITB,6500) S11, S22, S33, S23, S13, S12,
     $                   U1, V1, W1, U2, V2, W2, U3, V3, W3
      GO TO 900
  120 CONTINUE
C
C     *** CALLED FROM 'LATTIC' FOR SPECIAL CHECK RUN ONLY
C
C     --- WRITE HEADING FOR CHECK RUN, NUMBER OF PROBLEMS
      WRITE(IUNITB,7000)
      WRITE(IUNITB,7100) NTD
      GO TO 900
  130 CONTINUE
C
C     *** CALLED FROM 'OUTPT1' FOR CHECK RUN ONLY
C
C     --- WRITE PROBLEM NUMBER
      WRITE(IUNITB,7200) IPROB
  900 CONTINUE
      RETURN
 6100 FORMAT(1X,'MNCOND',I2,1X,6F12.6,3X,9F5.2)
 6200 FORMAT(1X,'SHORTV  ',1X,6F12.6,3X,9F5.2)
 6300 FORMAT(1X,'NORMAL',1X,I1,1X,6F12.6,3X,9F5.2)
 6400 FORMAT(1X,'SPCON2',2I1,1X,6F12.6,3X,9F5.2)
 6500 FORMAT(1X,'SPCON2  ',1X,6F12.6,3X,9F5.2)
 7000 FORMAT(///1X,'This mode of operation allows for the reduction of a
     $ large number'     /1X,'of cells (up to 99999) in a single run.  I
     $n this mode of operation,'     /1X,'the reduced cell, the transfor
     $mation matrix from the initial cell to'     /1X,'the reduced cell,
     $ and the problem number will be written on IUNITD'      /1X,'(Asso
     $ciated filename = NIST10,  Format = 6F10.6,2X,9F7.2,2X,I5).'/1X,
     $'NIST10 must not exist prior to execution and must be deleted afte
     $r'/1X,'program execution.  The printed output is limited to the pr
     $oblem'   /1X,'number followed by any warning and/or error messages
     $.')
 7100 FORMAT(//1X,'Number of cells to be reduced = ',I5//////)
 7200 FORMAT(1X,I5)
      END